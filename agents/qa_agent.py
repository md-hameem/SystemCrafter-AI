"""
SystemCrafter AI - QA Agent
Runs smoke tests and E2E tests on deployed applications.
"""
import asyncio
import json
from typing import Any

from agents.base import AgentConfig, BaseAgent
from orchestrator.core import get_logger

logger = get_logger(__name__)

SYSTEM_PROMPT = """You are a QA engineer. Generate Playwright E2E tests for the given endpoints and features.

Output ONLY valid JSON matching this schema:
{
  "smoke_test_results": [
    {
      "name": "Test name",
      "endpoint": "/api/endpoint",
      "method": "GET|POST",
      "status": "pass|fail",
      "response_time_ms": 123,
      "error": "Error message if failed"
    }
  ],
  "playwright_tests": {
    "tests/e2e/filename.spec.ts": "Playwright test file content"
  },
  "test_summary": {
    "total": 10,
    "passed": 8,
    "failed": 2,
    "skipped": 0
  },
  "recommendations": ["List of testing recommendations"]
}

PLAYWRIGHT TEST REQUIREMENTS:
- Use TypeScript
- Include page object model pattern
- Test authentication flows
- Test CRUD operations for main entities
- Include proper assertions
- Add screenshot on failure
- Use proper timeouts and waits"""


class QAAgent(BaseAgent):
    """
    Agent that runs quality assurance tests.
    """
    
    def __init__(self) -> None:
        config = AgentConfig(
            name="QA Agent",
            description="Runs smoke tests and generates E2E test suites",
            temperature=0.2,
            max_tokens=8192,
        )
        super().__init__(config)
    
    @property
    def system_prompt(self) -> str:
        return SYSTEM_PROMPT
    
    def build_user_prompt(self, input_data: dict) -> str:
        """Build prompt from endpoints."""
        endpoints = input_data.get("endpoints", {})
        tests = input_data.get("tests", [])
        
        prompt = f"Deployed Endpoints:\n{json.dumps(endpoints, indent=2)}"
        
        if tests:
            prompt += f"\n\nExisting Tests:\n{json.dumps(tests, indent=2)}"
        
        return prompt
    
    def validate_input(self, input_data: dict) -> bool:
        """Validate input."""
        return "endpoints" in input_data
    
    def validate_output(self, output: dict) -> bool:
        """Validate output."""
        return "smoke_test_results" in output
    
    def parse_response(self, response: str) -> dict:
        """Parse response."""
        try:
            return self._safe_json_parse(response)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response: {e}")
            raise ValueError(f"Invalid JSON response: {e}")
    
    async def run(self, input_data: dict) -> dict:
        """
        Run QA tests.
        
        1. Run smoke tests against endpoints
        2. Generate Playwright E2E tests
        """
        endpoints = input_data.get("endpoints", {})
        
        # Run actual smoke tests
        smoke_results = await self._run_smoke_tests(endpoints)
        
        # Generate E2E tests using LLM
        input_data["smoke_results"] = smoke_results
        llm_output = await super().run(input_data)
        
        # Combine results
        llm_output["smoke_test_results"] = smoke_results
        
        # Calculate summary
        passed = sum(1 for r in smoke_results if r["status"] == "pass")
        failed = sum(1 for r in smoke_results if r["status"] == "fail")
        
        llm_output["test_summary"] = {
            "total": len(smoke_results),
            "passed": passed,
            "failed": failed,
            "skipped": 0,
        }
        
        return llm_output
    
    async def _run_smoke_tests(self, endpoints: dict) -> list[dict]:
        """Run basic smoke tests against endpoints."""
        import httpx
        import time
        
        results = []
        
        for name, base_url in endpoints.items():
            # Test health endpoint
            health_result = await self._test_endpoint(
                f"{name} Health",
                f"{base_url}/health",
                "GET",
            )
            results.append(health_result)
            
            # Test root endpoint
            root_result = await self._test_endpoint(
                f"{name} Root",
                base_url,
                "GET",
            )
            results.append(root_result)
        
        return results
    
    async def _test_endpoint(
        self,
        name: str,
        url: str,
        method: str,
        expected_status: int = 200,
    ) -> dict:
        """Test a single endpoint."""
        import httpx
        import time
        
        result = {
            "name": name,
            "endpoint": url,
            "method": method,
            "status": "fail",
            "response_time_ms": 0,
            "error": None,
        }
        
        try:
            start = time.time()
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.request(method, url)
                result["response_time_ms"] = int((time.time() - start) * 1000)
                
                if response.status_code == expected_status:
                    result["status"] = "pass"
                else:
                    result["error"] = f"Expected {expected_status}, got {response.status_code}"
                    
        except Exception as e:
            result["error"] = str(e)
        
        return result
