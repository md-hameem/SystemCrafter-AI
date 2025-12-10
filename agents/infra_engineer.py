"""
SystemCrafter AI - Infrastructure Engineer Agent
Generates Dockerfiles, docker-compose, and infrastructure manifests.
"""
import json
from typing import Any

from agents.base import AgentConfig, BaseAgent
from orchestrator.core import get_logger

logger = get_logger(__name__)

SYSTEM_PROMPT = """You are a DevOps engineer. Generate complete infrastructure configuration files.

Output ONLY valid JSON matching this schema:
{
  "docker_compose": "Complete docker-compose.yml content as string",
  "dockerfiles": {
    "backend/Dockerfile": "Dockerfile content",
    "frontend/Dockerfile": "Dockerfile content"
  },
  "k8s_manifests": "Kubernetes manifests as YAML string (optional)",
  "terraform_skeleton": "Basic Terraform configuration (optional)",
  "nginx_config": "Nginx configuration if needed",
  "env_template": ".env.example template content"
}

DOCKER-COMPOSE REQUIREMENTS:
- Use version '3.8'
- Include all services: backend, frontend, database, redis
- Use proper networking (create a network)
- Include volumes for persistence
- Use environment variables with defaults
- Include health checks
- Set restart policies
- Expose only necessary ports
- Use build context for local development

DOCKERFILE REQUIREMENTS (Backend - Python/FastAPI):
- Use python:3.11-slim as base
- Use multi-stage build for smaller image
- Install dependencies with poetry or pip
- Run as non-root user
- Include health check
- Use proper PYTHONUNBUFFERED and PYTHONDONTWRITEBYTECODE

DOCKERFILE REQUIREMENTS (Frontend - Next.js):
- Use node:20-alpine as base
- Use multi-stage build (deps, builder, runner)
- Run as non-root user
- Optimize for production
- Include proper next.config.js settings

KUBERNETES SKELETON:
- Deployment for each service
- Service (ClusterIP) for internal communication
- Ingress for external access
- ConfigMaps and Secrets
- PersistentVolumeClaims for data

ENV TEMPLATE:
- Include all required environment variables
- Add comments explaining each variable
- Provide sensible defaults where appropriate"""


class InfraEngineerAgent(BaseAgent):
    """
    Agent that generates infrastructure configuration.
    """
    
    def __init__(self) -> None:
        config = AgentConfig(
            name="Infrastructure Engineer",
            description="Generates Docker, Kubernetes, and infrastructure configuration",
            temperature=0.1,
            max_tokens=8192,
        )
        super().__init__(config)
    
    @property
    def system_prompt(self) -> str:
        return SYSTEM_PROMPT
    
    def build_user_prompt(self, input_data: dict) -> str:
        """Build prompt from services list."""
        services = input_data.get("services", [])
        preferences = input_data.get("preferences", {})
        
        prompt = f"Services to deploy:\n{json.dumps(services, indent=2)}"
        
        if preferences:
            prompt += f"\n\nInfrastructure Preferences:\n{json.dumps(preferences, indent=2)}"
        
        return prompt
    
    def validate_input(self, input_data: dict) -> bool:
        """Validate that services are provided."""
        if "services" not in input_data:
            logger.error("Missing required field: services")
            return False
        return True
    
    def validate_output(self, output: dict) -> bool:
        """Validate output has required fields."""
        if "docker_compose" not in output:
            logger.error("Missing required output field: docker_compose")
            return False
        return True
    
    def parse_response(self, response: str) -> dict:
        """Parse JSON response from LLM."""
        try:
            return self._safe_json_parse(response)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response: {e}")
            raise ValueError(f"Invalid JSON response: {e}")
