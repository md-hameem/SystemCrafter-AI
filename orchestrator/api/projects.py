"""
SystemCrafter AI - Projects API Routes
"""
import uuid
from math import ceil
from typing import Annotated, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from orchestrator.api.auth import get_current_user
from orchestrator.core import get_db, get_logger
from orchestrator.models import Artifact, Project, ProjectSpec, User
from orchestrator.schemas import (
    ArtifactResponse,
    ProjectCreate,
    ProjectListResponse,
    ProjectResponse,
    ProjectSpecResponse,
    ProjectStatus,
    ProjectUpdate,
)
from orchestrator.services.orchestrator import OrchestratorService

router = APIRouter(prefix="/projects", tags=["Projects"])
logger = get_logger(__name__)


@router.post("/", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
async def create_project(
    project_data: ProjectCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> Project:
    """Create a new project and start the generation pipeline."""
    logger.info(
        "Creating new project",
        user_id=str(current_user.id),
        project_name=project_data.name,
    )
    
    # Create project
    project = Project(
        name=project_data.name,
        description=project_data.description,
        owner_id=current_user.id,
        stack_preferences=project_data.stack_preferences.model_dump() if project_data.stack_preferences else None,
        constraints=project_data.constraints.model_dump() if project_data.constraints else None,
        status=ProjectStatus.PENDING,
    )
    db.add(project)
    await db.flush()
    await db.refresh(project)
    
    # Start orchestration pipeline (async task)
    orchestrator = OrchestratorService(db)
    await orchestrator.start_pipeline(project)
    
    logger.info("Project created", project_id=str(project.id))
    return project


@router.get("/", response_model=ProjectListResponse)
async def list_projects(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
    status_filter: Optional[ProjectStatus] = None,
) -> dict:
    """List user's projects with pagination."""
    # Build query
    query = select(Project).where(Project.owner_id == current_user.id)
    count_query = select(func.count(Project.id)).where(Project.owner_id == current_user.id)
    
    if status_filter:
        query = query.where(Project.status == status_filter)
        count_query = count_query.where(Project.status == status_filter)
    
    # Get total count
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0
    
    # Get paginated results
    query = query.order_by(Project.created_at.desc())
    query = query.offset((page - 1) * size).limit(size)
    result = await db.execute(query)
    projects = result.scalars().all()
    
    return {
        "items": projects,
        "total": total,
        "page": page,
        "size": size,
        "pages": ceil(total / size) if total > 0 else 0,
    }


@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(
    project_id: uuid.UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> Project:
    """Get project details."""
    result = await db.execute(
        select(Project).where(
            Project.id == project_id,
            Project.owner_id == current_user.id,
        )
    )
    project = result.scalar_one_or_none()
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    return project


@router.patch("/{project_id}", response_model=ProjectResponse)
async def update_project(
    project_id: uuid.UUID,
    project_data: ProjectUpdate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> Project:
    """Update project details."""
    result = await db.execute(
        select(Project).where(
            Project.id == project_id,
            Project.owner_id == current_user.id,
        )
    )
    project = result.scalar_one_or_none()
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    # Update fields
    update_data = project_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        if value is not None:
            setattr(project, field, value)
    
    await db.flush()
    await db.refresh(project)
    
    return project


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(
    project_id: uuid.UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> None:
    """Delete a project and all associated data."""
    result = await db.execute(
        select(Project).where(
            Project.id == project_id,
            Project.owner_id == current_user.id,
        )
    )
    project = result.scalar_one_or_none()
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    await db.delete(project)
    logger.info("Project deleted", project_id=str(project_id))


@router.get("/{project_id}/spec", response_model=ProjectSpecResponse)
async def get_project_spec(
    project_id: uuid.UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> ProjectSpec:
    """Get the latest project specification."""
    # Verify ownership
    result = await db.execute(
        select(Project).where(
            Project.id == project_id,
            Project.owner_id == current_user.id,
        )
    )
    if not result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    # Get latest spec
    result = await db.execute(
        select(ProjectSpec)
        .where(ProjectSpec.project_id == project_id)
        .order_by(ProjectSpec.version.desc())
        .limit(1)
    )
    spec = result.scalar_one_or_none()
    
    if not spec:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project specification not found"
        )
    
    return spec


@router.get("/{project_id}/artifacts", response_model=list[ArtifactResponse])
async def list_project_artifacts(
    project_id: uuid.UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    artifact_type: Optional[str] = None,
) -> list[Artifact]:
    """List project artifacts."""
    # Verify ownership
    result = await db.execute(
        select(Project).where(
            Project.id == project_id,
            Project.owner_id == current_user.id,
        )
    )
    if not result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    # Get artifacts
    query = select(Artifact).where(Artifact.project_id == project_id)
    if artifact_type:
        query = query.where(Artifact.artifact_type == artifact_type)
    query = query.order_by(Artifact.created_at.desc())
    
    result = await db.execute(query)
    return result.scalars().all()


@router.post("/{project_id}/retry", response_model=ProjectResponse)
async def retry_project(
    project_id: uuid.UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> Project:
    """Retry a failed project generation."""
    result = await db.execute(
        select(Project).where(
            Project.id == project_id,
            Project.owner_id == current_user.id,
        )
    )
    project = result.scalar_one_or_none()
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    if project.status != ProjectStatus.FAILED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Can only retry failed projects"
        )
    
    # Reset status and restart
    project.status = ProjectStatus.PENDING
    await db.flush()
    
    orchestrator = OrchestratorService(db)
    await orchestrator.start_pipeline(project)
    
    await db.refresh(project)
    return project
