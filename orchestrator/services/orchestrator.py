"""
SystemCrafter AI - Orchestrator Service
Main service that coordinates all agents in the pipeline.
"""
import asyncio
import uuid
from datetime import datetime
from typing import Any, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from orchestrator.core import get_logger, get_settings
from orchestrator.models import AgentTask, Artifact, Project, ProjectSpec
from orchestrator.schemas import (
    AgentType,
    ProjectStatus,
    TaskStatus,
    WSEvent,
    WSEventType,
)
from orchestrator.services.websocket_manager import ws_manager

logger = get_logger(__name__)
settings = get_settings()


class OrchestratorService:
    """
    Orchestrator service that manages the project generation pipeline.
    Coordinates agents and maintains pipeline state.
    """
    
    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self._agents: dict[AgentType, Any] = {}
        self._initialize_agents()
    
    def _initialize_agents(self) -> None:
        """Initialize all agent instances."""
        # Import agents here to avoid circular imports
        from agents.requirement_interpreter import RequirementInterpreterAgent
        from agents.system_architect import SystemArchitectAgent
        from agents.api_designer import APIDesignerAgent
        from agents.db_designer import DBDesignerAgent
        from agents.backend_generator import BackendGeneratorAgent
        from agents.frontend_generator import FrontendGeneratorAgent
        from agents.infra_engineer import InfraEngineerAgent
        from agents.builder import BuilderAgent
        from agents.deployer import DeployerAgent
        from agents.qa_agent import QAAgent
        from agents.recovery_agent import RecoveryAgent
        
        self._agents = {
            AgentType.REQUIREMENT_INTERPRETER: RequirementInterpreterAgent(),
            AgentType.SYSTEM_ARCHITECT: SystemArchitectAgent(),
            AgentType.API_DESIGNER: APIDesignerAgent(),
            AgentType.DB_DESIGNER: DBDesignerAgent(),
            AgentType.BACKEND_GENERATOR: BackendGeneratorAgent(),
            AgentType.FRONTEND_GENERATOR: FrontendGeneratorAgent(),
            AgentType.INFRA_ENGINEER: InfraEngineerAgent(),
            AgentType.BUILDER: BuilderAgent(),
            AgentType.DEPLOYER: DeployerAgent(),
            AgentType.QA_AGENT: QAAgent(),
            AgentType.RECOVERY_AGENT: RecoveryAgent(),
        }
    
    async def start_pipeline(self, project: Project) -> None:
        """
        Start the project generation pipeline.
        This is the main entry point for project generation.
        """
        logger.info("Starting pipeline", project_id=str(project.id))
        
        # Run pipeline in background task
        asyncio.create_task(self._run_pipeline(project.id))
    
    async def _run_pipeline(self, project_id: uuid.UUID) -> None:
        """
        Execute the full pipeline for a project.
        Pipeline stages:
        1. Requirement Interpretation
        2. System Architecture
        3. API Design + DB Design (parallel)
        4. Backend Generation + Frontend Generation (parallel)
        5. Infrastructure Generation
        6. Build
        7. Deploy
        8. QA Tests
        """
        try:
            # Stage 1: Requirement Interpretation
            await self._update_project_status(project_id, ProjectStatus.ANALYZING)
            spec = await self._run_agent(
                project_id,
                AgentType.REQUIREMENT_INTERPRETER,
            )
            if not spec:
                await self._handle_pipeline_failure(project_id, "Failed to interpret requirements")
                return
            
            # Stage 2: System Architecture
            await self._update_project_status(project_id, ProjectStatus.DESIGNING)
            architecture = await self._run_agent(
                project_id,
                AgentType.SYSTEM_ARCHITECT,
                input_data={"project_spec": spec},
            )
            if not architecture:
                await self._handle_pipeline_failure(project_id, "Failed to design architecture")
                return
            
            # Stage 3: API Design + DB Design (parallel)
            api_task = self._run_agent(
                project_id,
                AgentType.API_DESIGNER,
                input_data={"project_spec": spec, "architecture": architecture},
            )
            db_task = self._run_agent(
                project_id,
                AgentType.DB_DESIGNER,
                input_data={"entities": spec.get("entities", [])},
            )
            
            api_design, db_design = await asyncio.gather(api_task, db_task)
            
            if not api_design or not db_design:
                await self._handle_pipeline_failure(project_id, "Failed to design API or database")
                return
            
            # Stage 4: Backend + Frontend Generation (parallel)
            await self._update_project_status(project_id, ProjectStatus.GENERATING)
            
            backend_task = self._run_agent(
                project_id,
                AgentType.BACKEND_GENERATOR,
                input_data={
                    "openapi_yaml": api_design.get("openapi_yaml"),
                    "sql_migration": db_design.get("sql_migration"),
                },
            )
            frontend_task = self._run_agent(
                project_id,
                AgentType.FRONTEND_GENERATOR,
                input_data={
                    "openapi_yaml": api_design.get("openapi_yaml"),
                    "ui_preferences": {},
                },
            )
            
            backend_output, frontend_output = await asyncio.gather(backend_task, frontend_task)
            
            if not backend_output or not frontend_output:
                await self._handle_pipeline_failure(project_id, "Failed to generate code")
                return
            
            # Stage 5: Infrastructure Generation
            infra_output = await self._run_agent(
                project_id,
                AgentType.INFRA_ENGINEER,
                input_data={
                    "services": [
                        {"name": "backend", "port": 8000},
                        {"name": "frontend", "port": 3000},
                        {"name": "db", "port": 5432},
                    ],
                },
            )
            
            if not infra_output:
                await self._handle_pipeline_failure(project_id, "Failed to generate infrastructure")
                return
            
            # Stage 6: Build
            await self._update_project_status(project_id, ProjectStatus.BUILDING)
            build_output = await self._run_agent(
                project_id,
                AgentType.BUILDER,
                input_data={"repo_path": f"./projects/{project_id}"},
            )
            
            if not build_output or build_output.get("status") == "failed":
                # Try recovery
                recovery_output = await self._run_agent(
                    project_id,
                    AgentType.RECOVERY_AGENT,
                    input_data={"logs": build_output.get("logs", "")},
                )
                if recovery_output:
                    # Apply patches and retry build
                    build_output = await self._run_agent(
                        project_id,
                        AgentType.BUILDER,
                        input_data={"repo_path": f"./projects/{project_id}"},
                    )
                
                if not build_output or build_output.get("status") == "failed":
                    await self._handle_pipeline_failure(project_id, "Build failed")
                    return
            
            # Stage 7: Deploy
            await self._update_project_status(project_id, ProjectStatus.DEPLOYING)
            deploy_output = await self._run_agent(
                project_id,
                AgentType.DEPLOYER,
                input_data={
                    "artifacts": build_output.get("artifacts", []),
                    "target": "docker-compose",
                },
            )
            
            if not deploy_output or deploy_output.get("status") == "failed":
                await self._handle_pipeline_failure(project_id, "Deployment failed")
                return
            
            # Stage 8: QA Tests
            qa_output = await self._run_agent(
                project_id,
                AgentType.QA_AGENT,
                input_data={"endpoints": deploy_output.get("endpoints", {})},
            )
            
            # Mark as completed
            await self._update_project_status(project_id, ProjectStatus.COMPLETED)
            
            logger.info("Pipeline completed successfully", project_id=str(project_id))
            
        except Exception as e:
            logger.exception("Pipeline failed with exception", project_id=str(project_id))
            await self._handle_pipeline_failure(project_id, str(e))
    
    async def _run_agent(
        self,
        project_id: uuid.UUID,
        agent_type: AgentType,
        input_data: Optional[dict] = None,
    ) -> Optional[dict]:
        """Run a single agent and store its output."""
        logger.info("Running agent", project_id=str(project_id), agent_type=agent_type.value)
        
        # Create task record
        task = AgentTask(
            project_id=project_id,
            agent_type=agent_type,
            status=TaskStatus.RUNNING,
            input_data=input_data,
            started_at=datetime.utcnow(),
        )
        self.db.add(task)
        await self.db.flush()
        
        # Broadcast task started
        await self._broadcast_event(
            project_id,
            WSEventType.TASK_STARTED,
            {"task_id": str(task.id), "agent_type": agent_type.value},
        )
        
        try:
            # Get agent and run
            agent = self._agents.get(agent_type)
            if not agent:
                raise ValueError(f"Unknown agent type: {agent_type}")
            
            # Prepare input (fetch project data if needed)
            if input_data is None:
                input_data = await self._get_agent_input(project_id, agent_type)
            
            # Execute agent
            output = await agent.run(input_data)
            
            # Update task
            task.status = TaskStatus.COMPLETED
            task.output_data = output
            task.completed_at = datetime.utcnow()
            task.duration_seconds = (task.completed_at - task.started_at).total_seconds()
            task.llm_prompt = getattr(agent, 'last_prompt', None)
            task.llm_response = getattr(agent, 'last_response', None)
            task.tokens_used = getattr(agent, 'last_tokens_used', None)
            
            await self.db.flush()
            
            # Store artifacts if generated
            await self._store_artifacts(project_id, task.id, agent_type, output)
            
            # Broadcast task completed
            await self._broadcast_event(
                project_id,
                WSEventType.TASK_COMPLETED,
                {"task_id": str(task.id), "agent_type": agent_type.value},
            )
            
            return output
            
        except Exception as e:
            logger.exception("Agent failed", project_id=str(project_id), agent_type=agent_type.value)
            
            task.status = TaskStatus.FAILED
            task.error_message = str(e)
            task.completed_at = datetime.utcnow()
            await self.db.flush()
            
            # Broadcast task failed
            await self._broadcast_event(
                project_id,
                WSEventType.TASK_FAILED,
                {
                    "task_id": str(task.id),
                    "agent_type": agent_type.value,
                    "error": str(e),
                },
            )
            
            return None
    
    async def _get_agent_input(
        self,
        project_id: uuid.UUID,
        agent_type: AgentType,
    ) -> dict:
        """Get input data for an agent based on project state."""
        from sqlalchemy import select
        
        if agent_type == AgentType.REQUIREMENT_INTERPRETER:
            # Get raw project description
            result = await self.db.execute(
                select(Project).where(Project.id == project_id)
            )
            project = result.scalar_one()
            return {
                "raw_text": project.description,
                "constraints": project.constraints or {},
            }
        
        # For other agents, input is provided by orchestrator
        return {}
    
    async def _store_artifacts(
        self,
        project_id: uuid.UUID,
        task_id: uuid.UUID,
        agent_type: AgentType,
        output: dict,
    ) -> None:
        """Store generated artifacts from agent output."""
        if not output:
            return
        
        artifacts_to_store = []
        
        # Extract artifacts based on agent type
        if agent_type == AgentType.API_DESIGNER and "openapi_yaml" in output:
            artifacts_to_store.append(
                Artifact(
                    project_id=project_id,
                    task_id=task_id,
                    artifact_type="openapi",
                    name="openapi.yaml",
                    content=output["openapi_yaml"],
                )
            )
        
        elif agent_type == AgentType.DB_DESIGNER:
            if "sql_migration" in output:
                artifacts_to_store.append(
                    Artifact(
                        project_id=project_id,
                        task_id=task_id,
                        artifact_type="sql",
                        name="migration.sql",
                        content=output["sql_migration"],
                    )
                )
            if "er_mermaid" in output:
                artifacts_to_store.append(
                    Artifact(
                        project_id=project_id,
                        task_id=task_id,
                        artifact_type="diagram",
                        name="er_diagram.mmd",
                        content=output["er_mermaid"],
                    )
                )
        
        elif agent_type in (AgentType.BACKEND_GENERATOR, AgentType.FRONTEND_GENERATOR):
            if "files" in output:
                for filename, content in output["files"].items():
                    artifacts_to_store.append(
                        Artifact(
                            project_id=project_id,
                            task_id=task_id,
                            artifact_type="code",
                            name=filename,
                            content=content if isinstance(content, str) else str(content),
                        )
                    )
        
        elif agent_type == AgentType.INFRA_ENGINEER:
            if "docker_compose" in output:
                artifacts_to_store.append(
                    Artifact(
                        project_id=project_id,
                        task_id=task_id,
                        artifact_type="docker",
                        name="docker-compose.yml",
                        content=output["docker_compose"],
                    )
                )
        
        # Store all artifacts
        for artifact in artifacts_to_store:
            self.db.add(artifact)
        
        if artifacts_to_store:
            await self.db.flush()
    
    async def _update_project_status(
        self,
        project_id: uuid.UUID,
        status: ProjectStatus,
    ) -> None:
        """Update project status."""
        from sqlalchemy import select
        
        result = await self.db.execute(
            select(Project).where(Project.id == project_id)
        )
        project = result.scalar_one()
        project.status = status
        
        if status == ProjectStatus.COMPLETED:
            project.completed_at = datetime.utcnow()
        
        await self.db.flush()
        
        # Broadcast status update
        await self._broadcast_event(
            project_id,
            WSEventType.PROJECT_STATUS,
            {"status": status.value},
        )
    
    async def _handle_pipeline_failure(
        self,
        project_id: uuid.UUID,
        error_message: str,
    ) -> None:
        """Handle pipeline failure."""
        logger.error("Pipeline failed", project_id=str(project_id), error=error_message)
        
        await self._update_project_status(project_id, ProjectStatus.FAILED)
        
        await self._broadcast_event(
            project_id,
            WSEventType.ERROR,
            {"message": error_message},
        )
    
    async def _broadcast_event(
        self,
        project_id: uuid.UUID,
        event_type: WSEventType,
        data: dict,
    ) -> None:
        """Broadcast event to WebSocket clients."""
        event = WSEvent(
            event_type=event_type,
            project_id=project_id,
            data=data,
        )
        await ws_manager.broadcast_to_project(str(project_id), event)
