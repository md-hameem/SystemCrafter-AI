"""
SystemCrafter AI - API Designer Agent
Produces OpenAPI 3.0 specifications for the selected architecture.
"""
import json
from typing import Any

from agents.base import AgentConfig, BaseAgent
from orchestrator.core import get_logger

logger = get_logger(__name__)

SYSTEM_PROMPT = """You are an expert API designer. Create a complete OpenAPI 3.0 YAML specification for the given project.

Output ONLY valid JSON matching this schema:
{
  "openapi_yaml": "Complete OpenAPI 3.0 YAML as a string",
  "endpoints_summary": [
    {
      "method": "GET|POST|PUT|PATCH|DELETE",
      "path": "/api/resource",
      "description": "What this endpoint does",
      "auth_required": true,
      "request_body": "Schema name or null",
      "response": "Schema name"
    }
  ],
  "schemas_summary": [
    {
      "name": "SchemaName",
      "description": "What this schema represents",
      "fields": ["field1", "field2"]
    }
  ],
  "auth_scheme": {
    "type": "jwt|oauth2|api_key",
    "description": "How authentication works"
  }
}

OPENAPI REQUIREMENTS:
- Use OpenAPI 3.0.3 format
- Include info section with title, version, description
- Define all paths with proper HTTP methods
- Include request/response schemas under components/schemas
- Add authentication scheme (prefer JWT Bearer)
- Include proper response codes (200, 201, 400, 401, 403, 404, 500)
- Add example payloads for requests and responses
- Include pagination for list endpoints (page, size, total)
- Use proper data types (string, integer, boolean, array, object)
- Add validation rules (minLength, maxLength, minimum, maximum, pattern)
- Group related endpoints using tags

ENDPOINTS TO INCLUDE:
- Authentication: POST /auth/register, POST /auth/login, GET /auth/me
- CRUD for each entity: GET (list), GET (detail), POST, PUT/PATCH, DELETE
- Any feature-specific endpoints

The openapi_yaml should be complete and valid YAML that can be parsed directly."""


class APIDesignerAgent(BaseAgent):
    """
    Agent that designs REST APIs and generates OpenAPI specifications.
    """
    
    def __init__(self) -> None:
        config = AgentConfig(
            name="API Designer",
            description="Designs REST APIs and generates OpenAPI specifications",
            temperature=0.1,  # Low temperature for consistent API design
            max_tokens=8192,  # Large output for complete OpenAPI spec
        )
        super().__init__(config)
    
    @property
    def system_prompt(self) -> str:
        return SYSTEM_PROMPT
    
    def build_user_prompt(self, input_data: dict) -> str:
        """Build prompt from project spec and architecture."""
        project_spec = input_data.get("project_spec", {})
        architecture = input_data.get("architecture", {})
        
        prompt = f"Project Specification:\n{json.dumps(project_spec, indent=2)}"
        
        if architecture:
            prompt += f"\n\nSelected Architecture:\n{json.dumps(architecture, indent=2)}"
        
        return prompt
    
    def validate_input(self, input_data: dict) -> bool:
        """Validate that project_spec is provided."""
        if "project_spec" not in input_data:
            logger.error("Missing required field: project_spec")
            return False
        return True
    
    def validate_output(self, output: dict) -> bool:
        """Validate output has required fields."""
        if "openapi_yaml" not in output:
            logger.error("Missing required output field: openapi_yaml")
            return False
        
        # Basic YAML validation
        openapi_yaml = output["openapi_yaml"]
        if not openapi_yaml or "openapi:" not in openapi_yaml:
            logger.error("Invalid OpenAPI YAML")
            return False
        
        return True
    
    def parse_response(self, response: str) -> dict:
        """Parse JSON response from LLM."""
        try:
            return self._safe_json_parse(response)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response: {e}")
            raise ValueError(f"Invalid JSON response: {e}")
