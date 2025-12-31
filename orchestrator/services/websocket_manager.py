"""
SystemCrafter AI - WebSocket Connection Manager
"""
import asyncio
from typing import Any

from fastapi import WebSocket

from orchestrator.core import get_logger
from orchestrator.schemas import WSEvent

logger = get_logger(__name__)


class WebSocketManager:
    """Manages WebSocket connections for real-time updates."""
    
    def __init__(self) -> None:
        # Map of project_id -> set of WebSocket connections
        self.active_connections: dict[str, set[WebSocket]] = {}
        self._lock = asyncio.Lock()
    
    async def connect(self, websocket: WebSocket, project_id: str) -> None:
        """Accept a new WebSocket connection."""
        await websocket.accept()
        async with self._lock:
            if project_id not in self.active_connections:
                self.active_connections[project_id] = set()
            self.active_connections[project_id].add(websocket)
    
    def disconnect(self, websocket: WebSocket, project_id: str) -> None:
        """Remove a WebSocket connection."""
        if project_id in self.active_connections:
            self.active_connections[project_id].discard(websocket)
            if not self.active_connections[project_id]:
                del self.active_connections[project_id]
    
    async def broadcast_to_project(
        self,
        project_id: str,
        event: WSEvent,
    ) -> None:
        """Broadcast an event to all connections for a project."""
        connection_count = len(self.active_connections.get(project_id, set()))
        logger.info(
            "Broadcasting WebSocket event",
            project_id=project_id,
            event_type=event.event_type,
            active_connections=connection_count,
        )
        
        if project_id not in self.active_connections:
            logger.warning("No active WebSocket connections for project", project_id=project_id)
            return
        
        message = event.model_dump_json()
        disconnected: list[WebSocket] = []
        
        for websocket in self.active_connections[project_id]:
            try:
                await websocket.send_text(message)
            except Exception as e:
                logger.warning(
                    "Failed to send WebSocket message",
                    project_id=project_id,
                    error=str(e),
                )
                disconnected.append(websocket)
        
        # Clean up disconnected sockets
        for ws in disconnected:
            self.disconnect(ws, project_id)
    
    async def send_personal(
        self,
        websocket: WebSocket,
        event: WSEvent,
    ) -> None:
        """Send an event to a specific connection."""
        try:
            await websocket.send_text(event.model_dump_json())
        except Exception as e:
            logger.warning("Failed to send personal WebSocket message", error=str(e))


# Global instance
ws_manager = WebSocketManager()
