"""
SystemCrafter AI - Base Agent Class
All agents inherit from this base class.
"""
import json
from abc import ABC, abstractmethod
from typing import Any, Optional

from pydantic import BaseModel

from orchestrator.core import get_logger, get_settings
from orchestrator.core.llm_client import LLMClient, get_llm

settings = get_settings()
logger = get_logger(__name__)


class AgentConfig(BaseModel):
    """Configuration for an agent."""
    name: str
    description: str
    model: str = "gpt-4-turbo-preview"
    temperature: float = 0.2
    max_tokens: int = 4096
    max_retries: int = 3


class BaseAgent(ABC):
    """
    Base class for all SystemCrafter agents.
    
    Each agent is responsible for a specific task in the pipeline:
    - Receives structured input
    - Processes using LLM and/or templates
    - Returns structured output
    """
    
    def __init__(self, config: AgentConfig) -> None:
        self.config = config
        self.llm_client: LLMClient = get_llm()
        
        # Audit trail
        self.last_prompt: Optional[str] = None
        self.last_response: Optional[str] = None
        self.last_tokens_used: Optional[int] = None
    
    @property
    @abstractmethod
    def system_prompt(self) -> str:
        """System prompt for the agent."""
        pass
    
    @abstractmethod
    def build_user_prompt(self, input_data: dict) -> str:
        """Build user prompt from input data."""
        pass
    
    @abstractmethod
    def validate_input(self, input_data: dict) -> bool:
        """Validate input data against schema."""
        pass
    
    @abstractmethod
    def validate_output(self, output: dict) -> bool:
        """Validate output data against schema."""
        pass
    
    @abstractmethod
    def parse_response(self, response: str) -> dict:
        """Parse LLM response into structured output."""
        pass
    
    async def run(self, input_data: dict) -> dict:
        """
        Execute the agent with given input.
        
        Args:
            input_data: Structured input matching agent's input schema
            
        Returns:
            Structured output matching agent's output schema
        """
        logger.info(f"Running agent: {self.config.name}")
        
        # Validate input
        if not self.validate_input(input_data):
            raise ValueError(f"Invalid input for {self.config.name}")
        
        # Build prompts
        user_prompt = self.build_user_prompt(input_data)
        self.last_prompt = f"SYSTEM: {self.system_prompt}\n\nUSER: {user_prompt}"
        
        # Call LLM with retries
        response = await self._call_llm_with_retry(user_prompt)
        self.last_response = response
        
        # Parse response
        output = self.parse_response(response)
        
        # Validate output
        if not self.validate_output(output):
            raise ValueError(f"Invalid output from {self.config.name}")
        
        logger.info(f"Agent {self.config.name} completed successfully")
        return output
    
    async def _call_llm_with_retry(self, user_prompt: str) -> str:
        """Call LLM with retry logic."""
        last_error = None
        
        for attempt in range(self.config.max_retries):
            try:
                # Use the abstracted LLM client for JSON responses
                result = await self.llm_client.generate_json(
                    prompt=user_prompt,
                    system_prompt=self.system_prompt,
                    temperature=self.config.temperature,
                    max_tokens=self.config.max_tokens,
                )
                
                # Return as JSON string for parsing
                return json.dumps(result)
                
            except Exception as e:
                last_error = e
                logger.warning(
                    f"LLM call failed (attempt {attempt + 1}/{self.config.max_retries})",
                    error=str(e),
                )
        
        raise RuntimeError(f"LLM call failed after {self.config.max_retries} attempts: {last_error}")
    
    def _safe_json_parse(self, text: str) -> dict:
        """Safely parse JSON from LLM response."""
        try:
            # Try direct parse
            return json.loads(text)
        except json.JSONDecodeError:
            # Try to extract JSON from markdown code blocks
            import re
            json_match = re.search(r'```(?:json)?\s*([\s\S]*?)\s*```', text)
            if json_match:
                return json.loads(json_match.group(1))
            raise
