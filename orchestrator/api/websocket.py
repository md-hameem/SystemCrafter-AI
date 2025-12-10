"""
SystemCrafter AI - WebSocket API for Real-time Updates
"""
import asyncio
import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect
from sqlalchemy.ext.asyncio import AsyncSession

from orchestrator.core import get_db, get_logger
from orchestrator.services.websocket_manager import WebSocketManager

router = APIRouter(prefix="/ws", tags=["WebSocket"])
logger = get_logger(__name__)

# Global WebSocket manager
ws_manager = WebSocketManager()


@router.websocket("/projects/{project_id}")
async def websocket_project_updates(
    websocket: WebSocket,
    project_id: uuid.UUID,
) -> None:
    """WebSocket endpoint for real-time project updates."""
    await ws_manager.connect(websocket, str(project_id))
    logger.info("WebSocket connected", project_id=str(project_id))
    
    try:
        while True:
            # Keep connection alive and handle incoming messages
            data = await websocket.receive_text()
            # Handle any client messages (ping/pong, etc.)
            if data == "ping":
                await websocket.send_text("pong")
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket, str(project_id))
        logger.info("WebSocket disconnected", project_id=str(project_id))
    except Exception as e:
        logger.error("WebSocket error", project_id=str(project_id), error=str(e))
        ws_manager.disconnect(websocket, str(project_id))
