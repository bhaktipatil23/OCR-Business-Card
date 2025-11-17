import asyncio
import json
from typing import Dict, List
from fastapi import WebSocket

class WebSocketManager:
    """Manage WebSocket connections for real-time updates"""
    
    def __init__(self):
        self._connections: Dict[str, List[WebSocket]] = {}
        self._lock = asyncio.Lock()
    
    async def connect(self, batch_id: str, websocket: WebSocket) -> None:
        """Add new WebSocket connection"""
        await websocket.accept()
        
        async with self._lock:
            if batch_id not in self._connections:
                self._connections[batch_id] = []
            self._connections[batch_id].append(websocket)
    
    async def disconnect(self, batch_id: str, websocket: WebSocket) -> None:
        """Remove WebSocket connection"""
        async with self._lock:
            if batch_id in self._connections:
                if websocket in self._connections[batch_id]:
                    self._connections[batch_id].remove(websocket)
                
                # Clean up empty batch
                if not self._connections[batch_id]:
                    del self._connections[batch_id]
    
    async def broadcast(self, batch_id: str, message: Dict) -> None:
        """Broadcast message to all connections for batch"""
        async with self._lock:
            if batch_id not in self._connections:
                return
            
            # Copy connections list to avoid modification during iteration
            connections = self._connections[batch_id].copy()
        
        # Send to all connections (outside lock to avoid blocking)
        dead_connections = []
        for websocket in connections:
            try:
                await websocket.send_text(json.dumps(message))
            except:
                dead_connections.append(websocket)
        
        # Remove dead connections
        if dead_connections:
            async with self._lock:
                if batch_id in self._connections:
                    for dead_ws in dead_connections:
                        if dead_ws in self._connections[batch_id]:
                            self._connections[batch_id].remove(dead_ws)
    
    async def send_initial_status(self, batch_id: str, websocket: WebSocket) -> None:
        """Send initial status when client connects"""
        from app.routers.upload import batch_storage
        from app.routers.process import file_status, file_lock
        
        if batch_id in batch_storage:
            files = batch_storage[batch_id]
            
            # Get file status if available
            current_status = {}
            with file_lock:
                if batch_id in file_status:
                    current_status = file_status[batch_id]
            
            await websocket.send_text(json.dumps({
                "type": "initial_status",
                "batch_id": batch_id,
                "total_files": len(files),
                "files": [{
                    "file_id": f["file_id"],
                    "filename": f["filename"],
                    "status": current_status.get(f["file_id"], {}).get("status", "waiting")
                } for f in files],
                "message": "Connected to WebSocket. Processing will start automatically."
            }))

# Global instance
websocket_manager = WebSocketManager()