"""
SystemCrafter AI - LLM Client Abstraction
Supports both OpenAI and Google Gemini
"""
import json
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
        pass
    
    @abstractmethod
    async def generate_json(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
    ) -> dict[str, Any]:
        """Generate JSON response from a prompt."""
        pass


class OpenAIClient(LLMClient):
    """OpenAI API client."""
    
    def __init__(self):
        from openai import AsyncOpenAI
        
        settings = get_settings()
        self.client = AsyncOpenAI(api_key=settings.openai_api_key)
        self.model = settings.llm_model
        self.default_temperature = settings.llm_temperature
        self.default_max_tokens = settings.llm_max_tokens
    
    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
    ) -> str:
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=temperature or self.default_temperature,
            max_tokens=max_tokens or self.default_max_tokens,
        )
        
        return response.choices[0].message.content or ""
    
    async def generate_json(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
    ) -> dict[str, Any]:
        json_system = (system_prompt or "") + "\n\nRespond with valid JSON only."
        
        messages = [
            {"role": "system", "content": json_system},
            {"role": "user", "content": prompt},
        ]
        
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=temperature or self.default_temperature,
            max_tokens=max_tokens or self.default_max_tokens,
            response_format={"type": "json_object"},
        )
        
        content = response.choices[0].message.content or "{}"
        return json.loads(content)


class GeminiClient(LLMClient):
    """Google Gemini API client using google-genai package."""
    
    def __init__(self):
        from google import genai
        
        settings = get_settings()
        self.client = genai.Client(api_key=settings.gemini_api_key)
        self.model_name = settings.llm_model
        self.default_temperature = settings.llm_temperature
        self.default_max_tokens = settings.llm_max_tokens
    
    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
    ) -> str:
        from google.genai import types
        
        # Build the full prompt with system instruction
        full_prompt = prompt
        if system_prompt:
            full_prompt = f"{system_prompt}\n\n{prompt}"
        
        config = types.GenerateContentConfig(
            temperature=temperature or self.default_temperature,
            max_output_tokens=max_tokens or self.default_max_tokens,
        )
        
        response = await self.client.aio.models.generate_content(
            model=self.model_name,
            contents=full_prompt,
            config=config,
        )
        
        return response.text or ""
    
    async def generate_json(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
    ) -> dict[str, Any]:
        from google.genai import types
        
        json_system = (system_prompt or "") + "\n\nRespond with valid JSON only. No markdown code blocks."
        full_prompt = f"{json_system}\n\n{prompt}"
        
        config = types.GenerateContentConfig(
            temperature=temperature or self.default_temperature,
            max_output_tokens=max_tokens or self.default_max_tokens,
            response_mime_type="application/json",
        )
        
        response = await self.client.aio.models.generate_content(
            model=self.model_name,
            contents=full_prompt,
            config=config,
        )
        
        content = response.text or "{}"
        # Clean up potential markdown formatting
        if content.startswith("```"):
            content = content.split("```")[1]
            if content.startswith("json"):
                content = content[4:]
        content = content.strip()
        
        return json.loads(content)


def get_llm_client() -> LLMClient:
    """Factory function to get the appropriate LLM client based on settings."""
    settings = get_settings()
    
    if settings.llm_provider == "gemini":
        logger.info("Using Google Gemini LLM client", model=settings.llm_model)
        return GeminiClient()
    else:
        logger.info("Using OpenAI LLM client", model=settings.llm_model)
        return OpenAIClient()


# Singleton instance
_llm_client: Optional[LLMClient] = None


def get_llm() -> LLMClient:
    """Get or create the singleton LLM client."""
    global _llm_client
    if _llm_client is None:
        _llm_client = get_llm_client()
    return _llm_client
