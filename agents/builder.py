"""
SystemCrafter AI - Builder Agent
Builds artifacts from generated code, runs linters/tests.
"""
import asyncio
import json
import os
import subprocess
from pathlib import Path
from typing import Any, Optional

from agents.base import AgentConfig, BaseAgent
from orchestrator.core import get_logger, get_settings

logger = get_logger(__name__)
settings = get_settings()


class BuilderAgent(BaseAgent):
    """
    Agent that builds project artifacts.
    This agent is primarily code-based (not LLM) but uses LLM for log summarization.
    """
    
    def __init__(self) -> None:
        config = AgentConfig(
            name="Builder",
            description="Builds project artifacts and runs tests",
            temperature=0.0,
            max_tokens=2048,
        )
        super().__init__(config)
    
    @property
    def system_prompt(self) -> str:
        return """You are a build system analyzer. Given build logs, summarize the results.
Output JSON: {"summary": "brief summary", "errors": ["list of errors"], "warnings": ["list of warnings"]}"""
    
    def build_user_prompt(self, input_data: dict) -> str:
        """Build prompt from build logs."""
        logs = input_data.get("logs", "")
        return f"Build logs:\n{logs}"
    
    def validate_input(self, input_data: dict) -> bool:
        """Validate input."""
        return "repo_path" in input_data
    
    def validate_output(self, output: dict) -> bool:
        """Validate output."""
        return "status" in output and "logs" in output
    
    def parse_response(self, response: str) -> dict:
        """Parse response."""
        try:
            return self._safe_json_parse(response)
        except:
            return {"summary": response, "errors": [], "warnings": []}
    
    async def run(self, input_data: dict) -> dict:
        """
        Build the project.
        
        1. Write generated files to disk
        2. Run linters (ruff, mypy for Python; eslint for JS)
        3. Run tests if available
        4. Build Docker images
        """
        repo_path = input_data.get("repo_path", "")
        logs = []
        status = "success"
        artifacts = []
        
        try:
            # Ensure directory exists
            project_dir = Path(repo_path)
            project_dir.mkdir(parents=True, exist_ok=True)
            
            logs.append(f"Building project at {repo_path}")
            
            # Check for backend
            backend_dir = project_dir / "backend"
            if backend_dir.exists():
                logs.append("Building backend...")
                
                # Run Python linter
                lint_result = await self._run_command(
                    ["python", "-m", "ruff", "check", "."],
                    cwd=str(backend_dir),
                )
                logs.append(f"Lint result: {lint_result}")
                
                # Run tests
                test_result = await self._run_command(
                    ["python", "-m", "pytest", "--tb=short"],
                    cwd=str(backend_dir),
                )
                logs.append(f"Test result: {test_result}")
                
                if "FAILED" in test_result or "error" in test_result.lower():
                    status = "warning"
            
            # Check for frontend
            frontend_dir = project_dir / "frontend"
            if frontend_dir.exists():
                logs.append("Building frontend...")
                
                # Install dependencies
                install_result = await self._run_command(
                    ["npm", "install"],
                    cwd=str(frontend_dir),
                )
                logs.append(f"npm install: {install_result[:500]}")
                
                # Build
                build_result = await self._run_command(
                    ["npm", "run", "build"],
                    cwd=str(frontend_dir),
                )
                logs.append(f"npm build: {build_result[:500]}")
                
                if "error" in build_result.lower():
                    status = "failed"
            
            # Build Docker images if docker-compose exists
            compose_file = project_dir / "docker-compose.yml"
            if compose_file.exists():
                logs.append("Building Docker images...")
                
                docker_result = await self._run_command(
                    ["docker-compose", "build"],
                    cwd=str(project_dir),
                )
                logs.append(f"Docker build: {docker_result[:1000]}")
                
                if "error" in docker_result.lower() and "warning" not in docker_result.lower():
                    status = "failed"
                else:
                    artifacts.append("docker-images")
            
            logs.append(f"Build completed with status: {status}")
            
        except Exception as e:
            logger.exception("Build failed")
            logs.append(f"Build error: {str(e)}")
            status = "failed"
        
        return {
            "status": status,
            "logs": "\n".join(logs),
            "artifacts": artifacts,
        }
    
    async def _run_command(
        self,
        cmd: list[str],
        cwd: str,
        timeout: int = 300,
    ) -> str:
        """Run a shell command and return output."""
        try:
            process = await asyncio.create_subprocess_exec(
                *cmd,
                cwd=cwd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.STDOUT,
            )
            
            stdout, _ = await asyncio.wait_for(
                process.communicate(),
                timeout=timeout,
            )
            
            return stdout.decode("utf-8", errors="replace")
            
        except asyncio.TimeoutError:
            return f"Command timed out after {timeout}s"
        except FileNotFoundError:
            return f"Command not found: {cmd[0]}"
        except Exception as e:
            return f"Command error: {str(e)}"
