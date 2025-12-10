"""
SystemCrafter AI - Requirement Interpreter Agent
Converts free-text product descriptions into structured project specifications.
"""
import json
from typing import Any

from agents.base import AgentConfig, BaseAgent
from orchestrator.core import get_logger

logger = get_logger(__name__)

SYSTEM_PROMPT = """You are a requirements engineer. Your job is to convert a free-text product description into a strict JSON Project Specification.

Output ONLY valid JSON that matches this schema:
{
  "title": "string (3-6 words)",
  "summary": "string (1-2 sentences)",
  "actors": ["string array of user roles"],
  "features": [
    {
      "id": "F1",
      "name": "Feature Name",
      "description": "Feature description",
      "acceptance_criteria": "How to verify feature works",
      "priority": "high|medium|low"
    }
  ],
  "entities": [
    {
      "name": "entity_name",
      "fields": [
        {"name": "field_name", "type": "string|int|uuid|datetime|float|boolean|json", "notes": "optional notes", "required": true, "unique": false}
      ],
      "relationships": [{"type": "belongs_to|has_many|has_one", "entity": "other_entity"}]
    }
  ],
  "nonfunctional": ["list of non-functional requirements like scalability, security, compliance"]
}

INSTRUCTIONS:
- Extract a short `title` (3-6 words)
- Create a `summary` (1-2 sentences)
- List primary `actors` (user roles)
- For `features`, provide comprehensive feature list with acceptance criteria
- For `entities`, identify all domain entities with their fields and relationships
- Populate `nonfunctional` with scaling/security/compliance items if mentioned
- Be thorough but realistic - focus on MVP scope
- Do NOT add explanatory text, only output valid JSON"""


class RequirementInterpreterAgent(BaseAgent):
    """
    Agent that interprets natural language product descriptions
    and produces structured project specifications.
    """
    
    def __init__(self) -> None:
        config = AgentConfig(
            name="Requirement Interpreter",
            description="Converts free-text product descriptions into structured specifications",
            temperature=0.1,  # Low temperature for consistent output
            max_tokens=4096,
        )
        super().__init__(config)
    
    @property
    def system_prompt(self) -> str:
        return SYSTEM_PROMPT
    
    def build_user_prompt(self, input_data: dict) -> str:
        """Build user prompt from raw text and constraints."""
        raw_text = input_data.get("raw_text", "")
        constraints = input_data.get("constraints", {})
        
        prompt = f"Product Description:\n{raw_text}"
        
        if constraints:
            prompt += f"\n\nConstraints and Preferences:\n{json.dumps(constraints, indent=2)}"
        
        return prompt
    
    def validate_input(self, input_data: dict) -> bool:
        """Validate that raw_text is provided."""
        if "raw_text" not in input_data:
            logger.error("Missing required field: raw_text")
            return False
        if not input_data["raw_text"].strip():
            logger.error("raw_text is empty")
            return False
        return True
    
    def validate_output(self, output: dict) -> bool:
        """Validate output has required fields."""
        required_fields = ["title", "features"]
        for field in required_fields:
            if field not in output:
                logger.error(f"Missing required output field: {field}")
                return False
        
        # Validate features structure
        if not isinstance(output.get("features"), list):
            logger.error("features must be a list")
            return False
        
        return True
    
    def parse_response(self, response: str) -> dict:
        """Parse JSON response from LLM."""
        try:
            return self._safe_json_parse(response)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response: {e}")
            raise ValueError(f"Invalid JSON response: {e}")
