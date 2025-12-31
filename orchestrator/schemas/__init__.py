"""
SystemCrafter AI - Pydantic Schemas for API
"""
import uuid
from datetime import datetime
from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field


# =============================================================================
# Enums
# =============================================================================

class ProjectStatus(str, Enum):
    PENDING = "pending"
    ANALYZING = "analyzing"
    DESIGNING = "designing"
    GENERATING = "generating"
    BUILDING = "building"
    DEPLOYING = "deploying"
    COMPLETED = "completed"
    FAILED = "failed"


class AgentType(str, Enum):
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
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    RETRYING = "retrying"


# =============================================================================
# User Schemas
# =============================================================================

class UserBase(BaseModel):
    email: EmailStr
    full_name: Optional[str] = None


class UserCreate(UserBase):
    password: str = Field(..., min_length=8)


class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    password: Optional[str] = Field(None, min_length=8)


class UserResponse(UserBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: uuid.UUID
    is_active: bool
    created_at: datetime


# =============================================================================
# Authentication Schemas
# =============================================================================

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenPayload(BaseModel):
    sub: str
    exp: datetime


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


# =============================================================================
# Project Schemas
# =============================================================================

class StackPreferences(BaseModel):
    """Stack configuration preferences."""
    backend: str = "fastapi"
    frontend: str = "nextjs"
    database: str = "postgres"
    cache: Optional[str] = "redis"
    deployment: str = "docker-compose"


class ProjectConstraints(BaseModel):
    """Project constraints and fixed preferences."""
    language: Optional[str] = None
    hosting: Optional[str] = None
    budget: Optional[str] = None
    timeline: Optional[str] = None
    compliance: Optional[list[str]] = None


class ProjectCreate(BaseModel):
    """Schema for creating a new project."""
    name: str = Field(..., min_length=1, max_length=255)
    description: str = Field(..., min_length=10)
    stack_preferences: Optional[StackPreferences] = None
    constraints: Optional[ProjectConstraints] = None


class ProjectUpdate(BaseModel):
    """Schema for updating a project."""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    stack_preferences: Optional[StackPreferences] = None
    constraints: Optional[ProjectConstraints] = None


class ProjectResponse(BaseModel):
    """Schema for project response."""
    model_config = ConfigDict(from_attributes=True)
    
    id: uuid.UUID
    name: str
    description: str
    status: ProjectStatus
    owner_id: uuid.UUID
    stack_preferences: Optional[dict] = None
    constraints: Optional[dict] = None
    repo_url: Optional[str] = None
    local_path: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime] = None


class ProjectListResponse(BaseModel):
    """Schema for paginated project list."""
    items: list[ProjectResponse]
    total: int
    page: int
    size: int
    pages: int


# =============================================================================
# Project Spec Schemas (Agent Outputs)
# =============================================================================

class FeatureSpec(BaseModel):
    """Feature specification."""
    id: str
    name: str
    description: str
    acceptance_criteria: Optional[str] = None
    priority: Optional[str] = "medium"


class EntityField(BaseModel):
    """Entity field definition."""
    name: str
    type: str
    notes: Optional[str] = None
    required: bool = True
    unique: bool = False


class EntitySpec(BaseModel):
    """Entity specification."""
    name: str
    fields: list[EntityField]
    relationships: Optional[list[dict]] = None


class ProjectSpecCreate(BaseModel):
    """Schema for creating project specification."""
    title: str
    summary: Optional[str] = None
    actors: Optional[list[str]] = None
    features: Optional[list[FeatureSpec]] = None
    entities: Optional[list[EntitySpec]] = None
    nonfunctional: Optional[list[str]] = None


class ProjectSpecResponse(BaseModel):
    """Schema for project specification response."""
    model_config = ConfigDict(from_attributes=True)
    
    id: uuid.UUID
    project_id: uuid.UUID
    version: int
    title: str
    summary: Optional[str] = None
    actors: Optional[list] = None
    features: Optional[list] = None
    entities: Optional[list] = None
    nonfunctional: Optional[list] = None
    architecture: Optional[dict] = None
    created_at: datetime


# =============================================================================
# Agent Task Schemas
# =============================================================================

class AgentTaskCreate(BaseModel):
    """Schema for creating an agent task."""
    agent_type: AgentType
    input_data: Optional[dict] = None


class AgentTaskResponse(BaseModel):
    """Schema for agent task response."""
    model_config = ConfigDict(from_attributes=True)
    
    id: uuid.UUID
    project_id: uuid.UUID
    agent_type: AgentType
    status: TaskStatus
    input_data: Optional[dict] = None
    output_data: Optional[dict] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    duration_seconds: Optional[float] = None
    error_message: Optional[str] = None
    retry_count: int
    created_at: datetime


# =============================================================================
# Artifact Schemas
# =============================================================================

class ArtifactCreate(BaseModel):
    """Schema for creating an artifact."""
    artifact_type: str
    name: str
    file_path: Optional[str] = None
    content: Optional[str] = None
    metadata: Optional[dict] = None


class ArtifactResponse(BaseModel):
    """Schema for artifact response."""
    model_config = ConfigDict(from_attributes=True)
    
    id: uuid.UUID
    project_id: uuid.UUID
    task_id: Optional[uuid.UUID] = None
    artifact_type: str
    name: str
    file_path: Optional[str] = None
    content: Optional[str] = None
    metadata: Optional[dict] = None
    created_at: datetime


# =============================================================================
# WebSocket Event Schemas
# =============================================================================

class WSEventType(str, Enum):
    PROJECT_STATUS = "project_status"
    TASK_STARTED = "task_started"
    TASK_PROGRESS = "task_progress"
    TASK_COMPLETED = "task_completed"
    TASK_FAILED = "task_failed"
    ARTIFACT_CREATED = "artifact_created"
    BUILD_LOG = "build_log"
    DEPLOY_LOG = "deploy_log"
    ERROR = "error"


class WSEvent(BaseModel):
    """WebSocket event message."""
    model_config = ConfigDict(populate_by_name=True)
    
    event_type: WSEventType = Field(..., serialization_alias="type")
    project_id: uuid.UUID
    data: dict[str, Any]
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    def model_dump_json(self, **kwargs):
        """Override to ensure project_id is serialized as string."""
        # Force by_alias to be True so event_type becomes 'type'
        kwargs.setdefault('by_alias', True)
        data = self.model_dump(**kwargs)
        # Convert UUID to string
        data['project_id'] = str(data['project_id'])
        import json
        return json.dumps(data, default=str)


# =============================================================================
# Health Check
# =============================================================================

class HealthCheck(BaseModel):
    """Health check response."""
    status: str = "healthy"
    version: str
    database: str = "connected"
    redis: str = "connected"
