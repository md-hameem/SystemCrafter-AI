"""
SystemCrafter AI - LLM Client Abstraction
Provides a minimal, well-formed implementation for Groq and lightweight
shims for Gemini/OpenAI so the application can import the module cleanly.
"""

import json
import asyncio
import re
import random
from abc import ABC, abstractmethod
from typing import Any, Optional

import structlog

from orchestrator.core.config import get_settings

logger = structlog.get_logger()


class LLMClient(ABC):
    """Abstract base class for LLM clients."""

    @abstractmethod
    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
    ) -> str:
        """Generate text from a prompt."""
        raise NotImplementedError()

    @abstractmethod
    async def generate_json(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
    ) -> dict[str, Any]:
        """Generate JSON response from a prompt."""
        raise NotImplementedError()


# Removed Gemini/OpenAI clients — this runtime only supports Groq.


class GroqClient(LLMClient):
    """Groq LLM client using the official Groq Python SDK.

    Calls to the sync SDK are executed in a thread via `asyncio.to_thread` so
    the rest of the application can `await` the results.
    """

    def __init__(self):
        try:
            from groq import Groq  # type: ignore
        except Exception as exc:  # pragma: no cover - best-effort import
            raise RuntimeError("Missing 'groq' package. Install it to use GROQ provider.") from exc

        settings = get_settings()
        api_key = settings.groq_api_key
        if not api_key:
            raise RuntimeError("GROQ API key (groq_api_key) is not set in configuration")

        self.client = Groq(api_key=api_key)
        self.model_name = settings.llm_model or "moonshotai/kimi-k2-instruct-0905"
        self.default_temperature = getattr(settings, "llm_temperature", 0.0)
        self.default_max_tokens = getattr(settings, "llm_max_tokens", 512)
        # Retry/backoff configuration
        self._retry_attempts = getattr(settings, "llm_retry_attempts", 5)
        self._retry_backoff = getattr(settings, "llm_retry_backoff_seconds", 5)

    async def _create_completion(self, prompt: str, temperature: float, max_tokens: int, stream: bool = False):
        def _call():
            return self.client.chat.completions.create(
                model=self.model_name,
                messages=[{"role": "user", "content": prompt}],
                temperature=temperature,
                max_completion_tokens=max_tokens,
                stream=stream,
            )

        last_exc = None
        for attempt in range(1, max(1, self._retry_attempts) + 1):
            try:
                return await asyncio.to_thread(_call)
            except Exception as exc:
                last_exc = exc
                # Try to respect Retry-After header when present on the exception
                retry_after = None
                try:
                    # Common SDKs attach the underlying response on the exception
                    resp = getattr(exc, "response", None) or exc.__dict__.get("response")
                    if resp is not None:
                        headers = getattr(resp, "headers", None) or getattr(resp, "headers", {})
                        if headers and isinstance(headers, dict):
                            retry_after = headers.get("Retry-After") or headers.get("retry-after")
                        else:
                            # Some response-like objects expose getheader/getheaders
                            retry_after = getattr(resp, "getheader", lambda k: None)("Retry-After")
                except Exception:
                    retry_after = None

                # Compute backoff: respect Retry-After when provided and parseable
                if retry_after:
                    try:
                        wait = float(retry_after)
                    except Exception:
                        try:
                            # If Retry-After is an HTTP date, fall back to exponential backoff
                            wait = self._retry_backoff * (2 ** (attempt - 1))
                        except Exception:
                            wait = self._retry_backoff
                else:
                    wait = self._retry_backoff * (2 ** (attempt - 1))

                # add jitter
                wait = wait + random.uniform(0, 1)

                logger.warning(
                    "Groq request failed, will retry",
                    attempt=attempt,
                    max_attempts=self._retry_attempts,
                    wait_seconds=wait,
                    error=str(exc),
                )

                if attempt == self._retry_attempts:
                    break
                await asyncio.sleep(wait)

        # final attempt failed
        raise RuntimeError(f"Groq LLM request failed after {self._retry_attempts} attempts: {last_exc}") from last_exc

    async def generate(self, prompt: str, system_prompt: Optional[str] = None, temperature: Optional[float] = None, max_tokens: Optional[int] = None) -> str:
        full_prompt = prompt if not system_prompt else f"{system_prompt}\n\n{prompt}"
        temperature = temperature or self.default_temperature
        max_tokens = max_tokens or self.default_max_tokens

        try:
            resp = await self._create_completion(full_prompt, temperature, max_tokens, stream=False)
        except Exception as exc:
            raise RuntimeError(f"Groq LLM request failed: {exc}") from exc

        try:
            if hasattr(resp, "choices"):
                first = resp.choices[0]
                if getattr(first, "message", None) and getattr(first.message, "content", None):
                    return first.message.content
                if getattr(first, "delta", None) and getattr(first.delta, "content", None):
                    return first.delta.content
            return str(resp)
        except Exception:
            return str(resp)

    async def generate_json(self, prompt: str, system_prompt: Optional[str] = None, temperature: Optional[float] = None, max_tokens: Optional[int] = None) -> dict[str, Any]:
        json_system = (system_prompt or "") + "\n\nRespond with valid JSON only. No markdown code blocks."
        full_prompt = f"{json_system}\n\n{prompt}"
        temperature = temperature or self.default_temperature
        max_tokens = max_tokens or self.default_max_tokens

        resp = await self._create_completion(full_prompt, temperature, max_tokens, stream=False)

        content = None
        try:
            if hasattr(resp, "choices"):
                first = resp.choices[0]
                if getattr(first, "message", None) and getattr(first.message, "content", None):
                    content = first.message.content
                elif getattr(first, "delta", None) and getattr(first.delta, "content", None):
                    content = first.delta.content
        except Exception:
            pass

        if not content:
            content = str(resp)

        # Normalize common wrappers (```json``` fences, generic triple-backticks)
        try:
            # remove ```json ... ``` blocks and replace with their inner content
            content = re.sub(r"```json\s*(.*?)\s*```", r"\1", content, flags=re.S | re.I)
            # remove other fenced codeblocks
            content = re.sub(r"```\s*(.*?)\s*```", r"\1", content, flags=re.S)
            # strip common markdown quoting
            content = content.strip()
        except Exception:
            pass

        # Try direct JSON parse first
        try:
            return json.loads(content)
        except Exception:
            # Try to be tolerant: extract the first JSON object or array-like substring
            m = re.search(r"(\{(?:.|\s)*\}|\[(?:.|\s)*\])", content, re.S)
            if m:
                candidate = m.group(0)
                # quick cleanup: remove trailing commas before closing braces/brackets
                candidate = re.sub(r",\s*(\}|\])", r"\1", candidate)
                try:
                    return json.loads(candidate)
                except Exception:
                    # final fallback: try to find the outermost braces
                    try:
                        start = content.find("{")
                        end = content.rfind("}")
                        if start != -1 and end != -1 and end > start:
                            candidate2 = content[start:end+1]
                            candidate2 = re.sub(r",\s*(\}|\])", r"\1", candidate2)
                            return json.loads(candidate2)
                    except Exception:
                        pass

        raise RuntimeError(f"Groq client failed to return valid JSON. Raw content: {content[:1000]!r}")


def get_llm_client() -> LLMClient:
    """Factory that returns an Ollama client instance. Ollama is the only supported provider."""
    settings = get_settings()

    class OllamaClient(LLMClient):
        """Simple Ollama client using the local Ollama HTTP API at localhost:11434."""

        def __init__(self):
            try:
                import requests
            except Exception as exc:
                raise RuntimeError("Missing 'requests' package. Install it to use Ollama provider.") from exc

            self._requests = requests
            self._base_url = getattr(settings, "ollama_base_url", "http://localhost:11434")
            self.model = settings.llm_model or "kimi-k2"
            self.default_temperature = getattr(settings, "llm_temperature", 0.0)
            self.default_max_tokens = getattr(settings, "llm_max_tokens", 2048)
            self._retry_attempts = getattr(settings, "llm_retry_attempts", 5)
            self._retry_backoff = getattr(settings, "llm_retry_backoff_seconds", 5)

        def _build_payload(self, prompt: str, temperature: float, max_tokens: int) -> dict:
            return {
                "model": self.model,
                "prompt": prompt,
                "temperature": temperature,
                "max_tokens": max_tokens,
            }

        async def _call_generate(self, prompt: str, temperature: float, max_tokens: int) -> str:
            def _post():
                endpoints = ["/api/generate", "/generate", "/v1/generate"]
                payload = self._build_payload(prompt, temperature, max_tokens)
                last_resp = None
                for ep in endpoints:
                    url = f"{self._base_url.rstrip('/')}{ep}"
                    try:
                        resp = self._requests.post(url, json=payload, timeout=120)
                        last_resp = resp
                        if resp.status_code == 404:
                            logger.warning("Ollama endpoint not found, trying next", url=url, status=resp.status_code)
                            continue
                        resp.raise_for_status()
                        return resp.text
                    except Exception:
                        # If it's an HTTP error other than 404, surface it to outer retry logic
                        if last_resp is not None and last_resp.status_code == 404:
                            continue
                        raise

                # If we exhausted endpoints and only saw 404s, raise a descriptive error
                if last_resp is not None and last_resp.status_code == 404:
                    raise self._requests.HTTPError(f"No Ollama generate endpoint found at {self._base_url} (tried {endpoints})")
                raise RuntimeError("Ollama _post failed without HTTP response")

            last_exc = None
            for attempt in range(1, max(1, self._retry_attempts) + 1):
                try:
                    return await asyncio.to_thread(_post)
                except Exception as exc:
                    last_exc = exc
                    retry_after = None
                    try:
                        resp = getattr(exc, "response", None)
                        if resp is None and hasattr(exc, "args") and exc.args:
                            resp = exc.args[0] if isinstance(exc.args[0], self._requests.Response) else None
                        if resp is not None:
                            headers = getattr(resp, "headers", {})
                            retry_after = headers.get("Retry-After") or headers.get("retry-after")
                    except Exception:
                        retry_after = None

                    if retry_after:
                        try:
                            wait = float(retry_after)
                        except Exception:
                            wait = self._retry_backoff * (2 ** (attempt - 1))
                    else:
                        wait = self._retry_backoff * (2 ** (attempt - 1))

                    wait = wait + random.uniform(0, 1)
                    logger.warning(
                        "Ollama request failed, will retry",
                        attempt=attempt,
                        max_attempts=self._retry_attempts,
                        wait_seconds=wait,
                        error=str(exc),
                    )

                    if attempt == self._retry_attempts:
                        break
                    await asyncio.sleep(wait)

            raise RuntimeError(f"Ollama request failed after {self._retry_attempts} attempts: {last_exc}") from last_exc

        async def generate(self, prompt: str, system_prompt: Optional[str] = None, temperature: Optional[float] = None, max_tokens: Optional[int] = None) -> str:
            full = prompt if not system_prompt else f"{system_prompt}\n\n{prompt}"
            temperature = temperature or self.default_temperature
            max_tokens = max_tokens or self.default_max_tokens
            return await self._call_generate(full, temperature, max_tokens)

        async def generate_json(self, prompt: str, system_prompt: Optional[str] = None, temperature: Optional[float] = None, max_tokens: Optional[int] = None) -> dict[str, Any]:
            full = (system_prompt or "") + "\n\nRespond with valid JSON only. No markdown code blocks." + "\n\n" + prompt
            text = await self._call_generate(full, temperature or self.default_temperature, max_tokens or self.default_max_tokens)

            try:
                text = re.sub(r"```json\s*(.*?)\s*```", r"\1", text, flags=re.S | re.I)
                text = re.sub(r"```\s*(.*?)\s*```", r"\1", text, flags=re.S)
                text = text.strip()
            except Exception:
                pass

            try:
                return json.loads(text)
            except Exception:
                m = re.search(r"(\{(?:.|\s)*\}|\[(?:.|\s)*\])", text, re.S)
                if m:
                    candidate = m.group(0)
                    candidate = re.sub(r",\s*(\}|\])", r"\1", candidate)
                    try:
                        return json.loads(candidate)
                    except Exception:
                        pass

            raise RuntimeError(f"Ollama client failed to return valid JSON. Raw: {text[:1000]!r}")

    # Always prefer Ollama for LLM operations
    try:
        client = OllamaClient()
        logger.info("Using Ollama LLM client", model=settings.llm_model)
        return client
    except Exception:
        logger.exception("Failed to initialize Ollama client")
        raise


# Singleton instance
_llm_client: Optional[LLMClient] = None


def get_llm() -> LLMClient:
    """Get or create the singleton LLM client."""
    global _llm_client
    if _llm_client is None:
        _llm_client = get_llm_client()
    return _llm_client

