"""
SystemCrafter AI - Recovery Agent
Analyzes failures and suggests patches.
"""
import json
from typing import Any

from agents.base import AgentConfig, BaseAgent
from orchestrator.core import get_logger

logger = get_logger(__name__)

SYSTEM_PROMPT = """You are an expert developer and debugger. Analyze failing build/deploy logs and suggest fixes.

Output ONLY valid JSON matching this schema:
{
  "diagnosis": {
    "root_cause": "Brief description of the root cause",
    "category": "syntax|dependency|configuration|runtime|network|permission",
    "severity": "critical|major|minor",
    "affected_files": ["list of affected files"]
  },
  "fixes": [
    {
      "description": "What this fix does",
      "file": "path/to/file",
      "action": "modify|create|delete",
      "priority": 1,
      "confidence": "high|medium|low"
    }
  ],
  "patches": [
    {
      "file": "path/to/file",
      "diff": "unified diff format showing the change"
    }
  ],
  "prevention": [
    "Suggestions to prevent this issue in the future"
  ],
  "additional_context": "Any additional helpful information"
}

ANALYSIS GUIDELINES:
- Look for common error patterns: import errors, syntax errors, missing dependencies
- Check for configuration issues: environment variables, file paths, ports
- Identify the exact line/file causing the issue
- Provide specific, actionable fixes
- Prioritize fixes by likelihood of success
- Include proper diffs that can be applied directly
- Suggest preventive measures

COMMON ISSUES TO CHECK:
- Missing __init__.py files
- Import path issues
- Missing environment variables
- Port conflicts
- Permission issues
- Missing dependencies in requirements.txt/package.json
- Dockerfile syntax errors
- YAML indentation issues"""


class RecoveryAgent(BaseAgent):
    """
    Agent that analyzes failures and suggests recovery patches.
    """
    
    def __init__(self) -> None:
        config = AgentConfig(
            name="Recovery Agent",
            description="Analyzes build/deploy failures and suggests fixes",
            temperature=0.2,
            max_tokens=4096,
        )
        super().__init__(config)
    
    @property
    def system_prompt(self) -> str:
        return SYSTEM_PROMPT
    
    def build_user_prompt(self, input_data: dict) -> str:
        """Build prompt from error logs."""
        logs = input_data.get("logs", "")
        context = input_data.get("context", {})
        
        prompt = f"Error Logs:\n```\n{logs}\n```"
        
        if context:
            prompt += f"\n\nAdditional Context:\n{json.dumps(context, indent=2)}"
        
        return prompt
    
    def validate_input(self, input_data: dict) -> bool:
        """Validate input."""
        if "logs" not in input_data:
            logger.error("Missing required field: logs")
            return False
        return True
    
    def validate_output(self, output: dict) -> bool:
        """Validate output."""
        required_fields = ["diagnosis", "fixes"]
        for field in required_fields:
            if field not in output:
                logger.error(f"Missing required output field: {field}")
                return False
        return True
    
    def parse_response(self, response: str) -> dict:
        """Parse response."""
        try:
            return self._safe_json_parse(response)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response: {e}")
            raise ValueError(f"Invalid JSON response: {e}")
