"""
SystemCrafter AI - Deployer Agent
Deploys built artifacts to target environment.
"""
import asyncio
import json
from pathlib import Path
from typing import Any

from agents.base import AgentConfig, BaseAgent
from orchestrator.core import get_logger, get_settings

logger = get_logger(__name__)
settings = get_settings()


class DeployerAgent(BaseAgent):
    """
    Agent that deploys built artifacts.
    Primarily code-based with LLM for error analysis.
    """
    
    def __init__(self) -> None:
        config = AgentConfig(
            name="Deployer",
            description="Deploys built artifacts to target environment",
            temperature=0.0,
            max_tokens=2048,
        )
        super().__init__(config)
    
    @property
    def system_prompt(self) -> str:
        return """You are a deployment analyzer. Given deployment logs, analyze the results.
Output JSON: {"status": "success|failed", "issues": ["list of issues"], "recommendations": ["list"]}"""
    
    def build_user_prompt(self, input_data: dict) -> str:
        """Build prompt from deployment logs."""
        logs = input_data.get("logs", "")
        return f"Deployment logs:\n{logs}"
    
    def validate_input(self, input_data: dict) -> bool:
        """Validate input."""
        return "artifacts" in input_data and "target" in input_data
    
    def validate_output(self, output: dict) -> bool:
        """Validate output."""
        return "status" in output and "endpoints" in output
    
    def parse_response(self, response: str) -> dict:
        """Parse response."""
        try:
            return self._safe_json_parse(response)
        except:
            return {"summary": response}
    
    async def run(self, input_data: dict) -> dict:
        """
        Deploy the project.
        
        Supported targets:
        - docker-compose: Local deployment
        - vercel: Vercel deployment (frontend)
        - kubernetes: K8s deployment
        """
        artifacts = input_data.get("artifacts", [])
        target = input_data.get("target", "docker-compose")
        project_path = input_data.get("project_path", f"{settings.projects_dir}/latest")
        
        logs = []
        status = "success"
        endpoints = {}
        
        try:
            logs.append(f"Deploying to {target}...")
            
            if target == "docker-compose":
                result = await self._deploy_docker_compose(project_path)
                logs.extend(result["logs"])
                status = result["status"]
                endpoints = result["endpoints"]
                
            elif target == "vercel":
                result = await self._deploy_vercel(project_path)
                logs.extend(result["logs"])
                status = result["status"]
                endpoints = result["endpoints"]
                
            elif target == "kubernetes":
                result = await self._deploy_kubernetes(project_path)
                logs.extend(result["logs"])
                status = result["status"]
                endpoints = result["endpoints"]
            
            else:
                logs.append(f"Unknown deployment target: {target}")
                status = "failed"
            
            # Health check
            if status == "success" and endpoints:
                health_result = await self._check_health(endpoints)
                logs.extend(health_result["logs"])
                if not health_result["healthy"]:
                    status = "warning"
            
        except Exception as e:
            logger.exception("Deployment failed")
            logs.append(f"Deployment error: {str(e)}")
            status = "failed"
        
        return {
            "status": status,
            "logs": logs,
            "endpoints": endpoints,
        }
    
    async def _deploy_docker_compose(self, project_path: str) -> dict:
        """Deploy using docker-compose."""
        logs = []
        status = "success"
        endpoints = {
            "backend": "http://localhost:8000",
            "frontend": "http://localhost:3000",
        }
        
        try:
            project_dir = Path(project_path)
            
            # Check for docker-compose.yml
            compose_file = project_dir / "docker-compose.yml"
            if not compose_file.exists():
                logs.append("docker-compose.yml not found")
                return {"logs": logs, "status": "failed", "endpoints": {}}
            
            # Stop any existing containers
            logs.append("Stopping existing containers...")
            await self._run_command(
                ["docker-compose", "down"],
                cwd=str(project_dir),
            )
            
            # Start containers
            logs.append("Starting containers...")
            result = await self._run_command(
                ["docker-compose", "up", "-d"],
                cwd=str(project_dir),
            )
            logs.append(result[:1000])
            
            if "error" in result.lower():
                status = "failed"
            else:
                logs.append("Containers started successfully")
                
                # Wait for services to be ready
                await asyncio.sleep(5)
                
        except Exception as e:
            logs.append(f"Docker compose error: {str(e)}")
            status = "failed"
        
        return {"logs": logs, "status": status, "endpoints": endpoints}
    
    async def _deploy_vercel(self, project_path: str) -> dict:
        """Deploy frontend to Vercel."""
        logs = ["Vercel deployment not yet implemented"]
        return {"logs": logs, "status": "skipped", "endpoints": {}}
    
    async def _deploy_kubernetes(self, project_path: str) -> dict:
        """Deploy to Kubernetes."""
        logs = ["Kubernetes deployment not yet implemented"]
        return {"logs": logs, "status": "skipped", "endpoints": {}}
    
    async def _check_health(self, endpoints: dict) -> dict:
        """Check health of deployed services."""
        import httpx
        
        logs = []
        healthy = True
        
        for name, url in endpoints.items():
            try:
                health_url = f"{url}/health"
                async with httpx.AsyncClient(timeout=10.0) as client:
                    response = await client.get(health_url)
                    if response.status_code == 200:
                        logs.append(f"✓ {name} is healthy at {url}")
                    else:
                        logs.append(f"✗ {name} returned {response.status_code}")
                        healthy = False
            except Exception as e:
                logs.append(f"✗ {name} health check failed: {str(e)}")
                healthy = False
        
        return {"logs": logs, "healthy": healthy}
    
    async def _run_command(
        self,
        cmd: list[str],
        cwd: str,
        timeout: int = 300,
    ) -> str:
        """Run a shell command."""
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
            
        except Exception as e:
            return f"Command error: {str(e)}"
