"""
SystemCrafter AI - Database Models
"""
import uuid
from datetime import datetime
from enum import Enum
from typing import Optional

from sqlalchemy import JSON, DateTime, ForeignKey, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from orchestrator.core.database import Base


class ProjectStatus(str, Enum):
    """Project lifecycle status."""
    PENDING = "pending"
    ANALYZING = "analyzing"
    DESIGNING = "designing"
    GENERATING = "generating"
    BUILDING = "building"
    DEPLOYING = "deploying"
    COMPLETED = "completed"
    FAILED = "failed"


class AgentType(str, Enum):
    """Types of agents in the system."""
    REQUIREMENT_INTERPRETER = "requirement_interpreter"
    SYSTEM_ARCHITECT = "system_architect"
    API_DESIGNER = "api_designer"
    DB_DESIGNER = "db_designer"
    BACKEND_GENERATOR = "backend_generator"
    FRONTEND_GENERATOR = "frontend_generator"
    INFRA_ENGINEER = "infra_engineer"
    BUILDER = "builder"
    DEPLOYER = "deployer"
    QA_AGENT = "qa_agent"
    RECOVERY_AGENT = "recovery_agent"


class TaskStatus(str, Enum):
    """Task execution status."""
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    RETRYING = "retrying"


class User(Base):
    """User account model."""
    __tablename__ = "users"
    
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255))
    full_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    is_active: Mapped[bool] = mapped_column(default=True)
    is_superuser: Mapped[bool] = mapped_column(default=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )
    
    # Relationships
    projects: Mapped[list["Project"]] = relationship(back_populates="owner")


class Project(Base):
    """Generated project model."""
    __tablename__ = "projects"
    
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String(255), index=True)
    description: Mapped[str] = mapped_column(Text)
    status: Mapped[ProjectStatus] = mapped_column(
        String(50),
        default=ProjectStatus.PENDING
    )
    
    # Owner
    owner_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE")
    )
    
    # Configuration
    stack_preferences: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    constraints: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    
    # Generated artifacts references
    repo_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    local_path: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )
    completed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )
    
    # Relationships
    owner: Mapped["User"] = relationship(back_populates="projects")
    specs: Mapped[list["ProjectSpec"]] = relationship(back_populates="project")
    tasks: Mapped[list["AgentTask"]] = relationship(back_populates="project")
    artifacts: Mapped[list["Artifact"]] = relationship(back_populates="project")


class ProjectSpec(Base):
    """Structured project specification from requirement interpreter."""
    __tablename__ = "project_specs"
    
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    project_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("projects.id", ondelete="CASCADE")
    )
    version: Mapped[int] = mapped_column(default=1)
    
    # Specification content
    title: Mapped[str] = mapped_column(String(255))
    summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    actors: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)
    features: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)
    entities: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)
    nonfunctional: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)
    
    # Architecture decision
    architecture: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now()
    )
    
    # Relationships
    project: Mapped["Project"] = relationship(back_populates="specs")


class AgentTask(Base):
    """Task executed by an agent."""
    __tablename__ = "agent_tasks"
    
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    project_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("projects.id", ondelete="CASCADE")
    )
    agent_type: Mapped[AgentType] = mapped_column(String(50))
    status: Mapped[TaskStatus] = mapped_column(String(50), default=TaskStatus.QUEUED)
    
    # Input/Output
    input_data: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    output_data: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    
    # Execution details
    started_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )
    completed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )
    duration_seconds: Mapped[Optional[float]] = mapped_column(nullable=True)
    
    # Error handling
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    retry_count: Mapped[int] = mapped_column(default=0)
    max_retries: Mapped[int] = mapped_column(default=3)
    
    # Audit
    llm_prompt: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    llm_response: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    tokens_used: Mapped[Optional[int]] = mapped_column(nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now()
    )
    
    # Relationships
    project: Mapped["Project"] = relationship(back_populates="tasks")


class Artifact(Base):
    """Generated artifact (file, diagram, etc.)."""
    __tablename__ = "artifacts"
    
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    project_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("projects.id", ondelete="CASCADE")
    )
    task_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("agent_tasks.id", ondelete="SET NULL"),
        nullable=True
    )
    
    # Artifact details
    artifact_type: Mapped[str] = mapped_column(String(100))  # openapi, schema, code, dockerfile, etc.
    name: Mapped[str] = mapped_column(String(255))
    file_path: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    content: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    content_hash: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    
    # Metadata
    artifact_metadata: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now()
    )
    
    # Relationships
    project: Mapped["Project"] = relationship(back_populates="artifacts")


class AuditLog(Base):
    """Audit log for tracking all system actions."""
    __tablename__ = "audit_logs"
    
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    user_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        nullable=True
    )
    project_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        nullable=True
    )
    
    action: Mapped[str] = mapped_column(String(100))
    resource_type: Mapped[str] = mapped_column(String(100))
    resource_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    details: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now()
    )
