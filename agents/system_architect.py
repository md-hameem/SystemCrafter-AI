"""
SystemCrafter AI - System Architect Agent
Recommends architecture patterns and generates high-level diagrams.
"""
import json
from typing import Any

from agents.base import AgentConfig, BaseAgent
from orchestrator.core import get_logger

logger = get_logger(__name__)

SYSTEM_PROMPT = """You are a senior systems architect. Given a ProjectSpec, propose architecture options and select the best one.

Output ONLY valid JSON matching this schema:
{
  "architecture_options": [
    {
      "name": "Monolith|Microservices|Event-Driven|Serverless",
      "description": "Brief description",
      "pros": ["list of advantages"],
      "cons": ["list of disadvantages"],
      "complexity": "low|medium|high",
      "estimated_cost": "low|medium|high",
      "recommended_for": "Description of when to use this"
    }
  ],
  "selected_architecture": {
    "name": "Selected architecture name",
    "rationale": "Why this was selected",
    "services": [
      {
        "name": "service_name",
        "type": "api|web|worker|database|cache|queue",
        "description": "Service purpose",
        "technology": "FastAPI|Next.js|Postgres|Redis|etc",
        "port": 8000
      }
    ],
    "communication": "REST|GraphQL|gRPC|Events",
    "data_flow": "Description of how data flows between services"
  },
  "diagram_mermaid": "Mermaid flowchart or architecture diagram code",
  "infrastructure_requirements": {
    "database": "postgres|mysql|mongodb",
    "cache": "redis|memcached|none",
    "queue": "redis|rabbitmq|kafka|none",
    "storage": "s3|local|none"
  },
  "security_considerations": ["List of security aspects to implement"],
  "scaling_strategy": "Description of how to scale"
}

INSTRUCTIONS:
- Analyze the ProjectSpec to understand requirements
- Propose 2-3 realistic architecture options with honest pros/cons
- Select the most appropriate architecture for the given requirements
- For MVP projects, prefer simpler architectures (monolith or modular monolith)
- Generate a Mermaid diagram showing services and data flows
- Include practical security and scaling considerations"""


class SystemArchitectAgent(BaseAgent):
    """
    Agent that designs system architecture based on project specifications.
    """
    
    def __init__(self) -> None:
        config = AgentConfig(
            name="System Architect",
            description="Designs system architecture and generates diagrams",
            temperature=0.3,  # Slightly higher for creative architecture decisions
            max_tokens=4096,
        )
        super().__init__(config)
    
    @property
    def system_prompt(self) -> str:
        return SYSTEM_PROMPT
    
    def build_user_prompt(self, input_data: dict) -> str:
        """Build prompt from project spec."""
        project_spec = input_data.get("project_spec", {})
        preferences = input_data.get("preferences", {})
        
        prompt = f"Project Specification:\n{json.dumps(project_spec, indent=2)}"
        
        if preferences:
            prompt += f"\n\nArchitecture Preferences:\n{json.dumps(preferences, indent=2)}"
        
        return prompt
    
    def validate_input(self, input_data: dict) -> bool:
        """Validate that project_spec is provided."""
        if "project_spec" not in input_data:
            logger.error("Missing required field: project_spec")
            return False
        return True
    
    def validate_output(self, output: dict) -> bool:
        """Validate output has required fields."""
        required_fields = ["selected_architecture", "diagram_mermaid"]
        for field in required_fields:
            if field not in output:
                logger.error(f"Missing required output field: {field}")
                return False
        return True
    
    def parse_response(self, response: str) -> dict:
        """Parse JSON response from LLM."""
        try:
            return self._safe_json_parse(response)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response: {e}")
            raise ValueError(f"Invalid JSON response: {e}")
