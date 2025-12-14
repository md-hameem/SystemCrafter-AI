"""
SystemCrafter AI - LLM Client Abstraction
Provides a minimal, well-formed implementation for Groq and lightweight
shims for Gemini/OpenAI so the application can import the module cleanly.
"""

import json
import asyncio
import re
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

    async def _create_completion(self, prompt: str, temperature: float, max_tokens: int, stream: bool = False):
        def _call():
            return self.client.chat.completions.create(
                model=self.model_name,
                messages=[{"role": "user", "content": prompt}],
                temperature=temperature,
                max_completion_tokens=max_tokens,
                stream=stream,
            )

        return await asyncio.to_thread(_call)

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

        try:
            return json.loads(content)
        except Exception:
            m = re.search(r"\{.*\}", content, re.S)
            if m:
                try:
                    return json.loads(m.group(0))
                except Exception:
                    pass

        raise RuntimeError("Groq client failed to return valid JSON")


def get_llm_client() -> LLMClient:
    """Factory that returns the Groq client — OpenAI/Gemini removed."""
    settings = get_settings()
    provider = (settings.llm_provider or "").lower()

    if provider and provider != "groq":
        logger.warning("LLM provider configured as '%s' but only 'groq' is supported — overriding to 'groq'", provider)

    logger.info("Using Groq LLM client", model=settings.llm_model)
    return GroqClient()


# Singleton instance
_llm_client: Optional[LLMClient] = None


def get_llm() -> LLMClient:
    """Get or create the singleton LLM client."""
    global _llm_client
    if _llm_client is None:
        _llm_client = get_llm_client()
    return _llm_client

