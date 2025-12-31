"""
SystemCrafter AI - WebSocket API for Real-time Updates
"""
import asyncio
import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect
from sqlalchemy.ext.asyncio import AsyncSession

from orchestrator.core import get_db, get_logger, decode_access_token
from orchestrator.services.websocket_manager import ws_manager

router = APIRouter(prefix="/ws", tags=["WebSocket"])
logger = get_logger(__name__)

# Connection logic uses the global ws_manager instance imported above


@router.websocket("/projects/{project_id}")
async def websocket_project_updates(
    websocket: WebSocket,
    project_id: uuid.UUID,
) -> None:
    """WebSocket endpoint for real-time project updates."""
    # Validate optional token query param for authenticated connections
    token = websocket.query_params.get("token")
    if token:
        token_data = decode_access_token(token)
        if token_data is None:
            # Reject unauthorized client with policy violation code
            await websocket.close(code=1008)
            logger.info("WebSocket rejected - invalid token", project_id=str(project_id))
            return

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


# Alias route to support clients connecting to `/ws/{project_id}` without the
# `projects` segment (some frontend code uses this path). Keep identical
# behavior and token validation.
@router.websocket("/{project_id}")
async def websocket_project_updates_alias(
    websocket: WebSocket,
    project_id: uuid.UUID,
) -> None:
    token = websocket.query_params.get("token")
    if token:
        token_data = decode_access_token(token)
        if token_data is None:
            await websocket.close(code=1008)
            logger.info("WebSocket alias rejected - invalid token", project_id=str(project_id))
            return

    await ws_manager.connect(websocket, str(project_id))
    logger.info("WebSocket alias connected", project_id=str(project_id))

    try:
        while True:
            data = await websocket.receive_text()
            if data == "ping":
                await websocket.send_text("pong")
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket, str(project_id))
        logger.info("WebSocket alias disconnected", project_id=str(project_id))
    except Exception as e:
        logger.error("WebSocket alias error", project_id=str(project_id), error=str(e))
        ws_manager.disconnect(websocket, str(project_id))
