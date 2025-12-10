"""
SystemCrafter AI - Tasks API Routes
"""
import uuid
from typing import Annotated, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from orchestrator.api.auth import get_current_user
from orchestrator.core import get_db
from orchestrator.models import AgentTask, Project, User
from orchestrator.schemas import AgentTaskResponse, AgentType, TaskStatus

router = APIRouter(prefix="/tasks", tags=["Tasks"])


@router.get("/project/{project_id}", response_model=list[AgentTaskResponse])
async def list_project_tasks(
    project_id: uuid.UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    agent_type: Optional[AgentType] = None,
    status_filter: Optional[TaskStatus] = None,
) -> list[AgentTask]:
    """List all tasks for a project."""
    # Verify project ownership
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
    
    # Build query
    query = select(AgentTask).where(AgentTask.project_id == project_id)
    
    if agent_type:
        query = query.where(AgentTask.agent_type == agent_type)
    if status_filter:
        query = query.where(AgentTask.status == status_filter)
    
    query = query.order_by(AgentTask.created_at.desc())
    
    result = await db.execute(query)
    return result.scalars().all()


@router.get("/{task_id}", response_model=AgentTaskResponse)
async def get_task(
    task_id: uuid.UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> AgentTask:
    """Get task details."""
    result = await db.execute(
        select(AgentTask)
        .join(Project)
        .where(
            AgentTask.id == task_id,
            Project.owner_id == current_user.id,
        )
    )
    task = result.scalar_one_or_none()
    
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    return task


@router.get("/{task_id}/logs")
async def get_task_logs(
    task_id: uuid.UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> dict:
    """Get task execution logs (LLM prompt and response)."""
    result = await db.execute(
        select(AgentTask)
        .join(Project)
        .where(
            AgentTask.id == task_id,
            Project.owner_id == current_user.id,
        )
    )
    task = result.scalar_one_or_none()
    
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    return {
        "task_id": str(task.id),
        "agent_type": task.agent_type,
        "llm_prompt": task.llm_prompt,
        "llm_response": task.llm_response,
        "tokens_used": task.tokens_used,
        "error_message": task.error_message,
    }
