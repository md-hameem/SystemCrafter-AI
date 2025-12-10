"""
SystemCrafter AI - Backend Generator Agent
Generates FastAPI backend code from OpenAPI spec and DB schema.
"""
import json
from typing import Any

from agents.base import AgentConfig, BaseAgent
from orchestrator.core import get_logger

logger = get_logger(__name__)

SYSTEM_PROMPT = """You are a backend engineer. Generate a complete FastAPI backend application.

Output ONLY valid JSON matching this schema:
{
  "files": {
    "path/to/file.py": "file content as string",
    "path/to/another.py": "file content"
  },
  "entrypoint": "app/main.py",
  "dependencies": ["fastapi", "uvicorn", "sqlalchemy", "etc"],
  "tests": {
    "tests/test_file.py": "test file content"
  },
  "structure": {
    "description": "Brief description of the project structure"
  }
}

BACKEND STRUCTURE (FastAPI):
app/
├── __init__.py
├── main.py              # FastAPI app entry point
├── core/
│   ├── __init__.py
│   ├── config.py        # Settings from environment
│   ├── database.py      # SQLAlchemy setup
│   └── security.py      # JWT/auth utilities
├── models/
│   ├── __init__.py
│   └── *.py             # SQLAlchemy models
├── schemas/
│   ├── __init__.py
│   └── *.py             # Pydantic schemas
├── api/
│   ├── __init__.py
│   ├── deps.py          # Dependencies (get_db, get_current_user)
│   └── routes/
│       ├── __init__.py
│       ├── auth.py
│       └── *.py         # Route handlers
├── services/
│   ├── __init__.py
│   └── *.py             # Business logic
└── utils/
    └── __init__.py

REQUIREMENTS:
- Use async/await throughout
- Use SQLAlchemy 2.0 async style
- Implement proper error handling with HTTPException
- Use Pydantic v2 for request/response validation
- Implement JWT authentication with python-jose
- Include proper CORS configuration
- Add health check endpoint
- Use dependency injection for database sessions
- Include proper logging with structlog
- Generate basic unit tests for models and endpoints
- Follow PEP 8 style guidelines
- Include type hints everywhere
- Add docstrings to all functions and classes

Generate code that directly implements the OpenAPI spec provided."""


class BackendGeneratorAgent(BaseAgent):
    """
    Agent that generates FastAPI backend code.
    """
    
    def __init__(self) -> None:
        config = AgentConfig(
            name="Backend Generator",
            description="Generates FastAPI backend code from specifications",
            temperature=0.2,
            max_tokens=16384,  # Large output for complete backend
        )
        super().__init__(config)
    
    @property
    def system_prompt(self) -> str:
        return SYSTEM_PROMPT
    
    def build_user_prompt(self, input_data: dict) -> str:
        """Build prompt from OpenAPI and SQL migration."""
        openapi_yaml = input_data.get("openapi_yaml", "")
        sql_migration = input_data.get("sql_migration", "")
        preferences = input_data.get("preferences", {})
        
        prompt = f"OpenAPI Specification:\n```yaml\n{openapi_yaml}\n```"
        prompt += f"\n\nDatabase Schema:\n```sql\n{sql_migration}\n```"
        
        if preferences:
            prompt += f"\n\nPreferences:\n{json.dumps(preferences, indent=2)}"
        
        return prompt
    
    def validate_input(self, input_data: dict) -> bool:
        """Validate that OpenAPI and SQL are provided."""
        if "openapi_yaml" not in input_data:
            logger.error("Missing required field: openapi_yaml")
            return False
        if "sql_migration" not in input_data:
            logger.error("Missing required field: sql_migration")
            return False
        return True
    
    def validate_output(self, output: dict) -> bool:
        """Validate output has required fields."""
        if "files" not in output:
            logger.error("Missing required output field: files")
            return False
        if not isinstance(output["files"], dict):
            logger.error("files must be a dictionary")
            return False
        if len(output["files"]) == 0:
            logger.error("files dictionary is empty")
            return False
        return True
    
    def parse_response(self, response: str) -> dict:
        """Parse JSON response from LLM."""
        try:
            return self._safe_json_parse(response)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response: {e}")
            raise ValueError(f"Invalid JSON response: {e}")
