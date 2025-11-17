from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.services.websocket_manager import websocket_manager
from app.routers.upload import batch_storage, validation_storage
from app.routers.process import process_files_individually
import asyncio

router = APIRouter(tags=["websocket"])

@router.websocket("/ws/{batch_id}")
async def websocket_endpoint(websocket: WebSocket, batch_id: str):
    """WebSocket endpoint that auto-starts existing processing"""
    await websocket_manager.connect(batch_id, websocket)
    
    try:
        # Send initial status
        await websocket_manager.send_initial_status(batch_id, websocket)
        
        # Auto-start existing processing workflow
        if batch_id in batch_storage and batch_id in validation_storage:
            asyncio.create_task(process_files_individually(batch_id))
        
        # Keep connection alive
        while True:
            try:
                data = await websocket.receive_text()
                if data == "ping":
                    await websocket.send_text("pong")
                elif data == "start_processing":
                    # Client can manually trigger processing
                    if batch_id in batch_storage and batch_id in validation_storage:
                        asyncio.create_task(process_files_individually(batch_id))
            except:
                break
                
    except WebSocketDisconnect:
        pass
    finally:
        await websocket_manager.disconnect(batch_id, websocket)