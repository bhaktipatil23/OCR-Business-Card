from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from app.services.queue_manager import queue_manager
from app.services.websocket_manager import websocket_manager
import asyncio
import time

router = APIRouter(prefix="/api/v1", tags=["process"])

class ProcessSingleRequest(BaseModel):
    batch_id: str
    file_id: str

@router.post("/process-single")
async def process_single_file(request: ProcessSingleRequest, background_tasks: BackgroundTasks):
    """Start processing single file"""
    
    # Validate file exists in input queue
    file_pair = queue_manager.get_file_pair(request.batch_id, request.file_id)
    if not file_pair["input"]:
        raise HTTPException(status_code=404, detail="File not found in queue")
    
    if file_pair["input"]["status"] != "waiting":
        raise HTTPException(status_code=400, detail="File already processed or processing")
    
    # Start background processing
    background_tasks.add_task(process_single_file_with_updates, request.batch_id, request.file_id)
    
    return {
        "status": "started",
        "batch_id": request.batch_id,
        "file_id": request.file_id,
        "filename": file_pair["input"]["filename"],
        "message": "Processing started"
    }

async def process_single_file_with_updates(batch_id: str, file_id: str):
    """Process single file with WebSocket updates"""
    
    try:
        # Get file from input queue
        file_pair = queue_manager.get_file_pair(batch_id, file_id)
        if not file_pair["input"]:
            return
        
        file_info = file_pair["input"]
        start_time = time.time()
        
        # Stage 1: Start processing
        queue_manager.update_input_status(batch_id, file_id, "processing")
        await websocket_manager.broadcast(batch_id, {
            "type": "file_update",
            "file_id": file_id,
            "filename": file_info["filename"],
            "status": "processing",
            "stage": "started",
            "progress": 0
        })
        
        # Stage 2: Validation (2-3s)
        queue_manager.update_input_status(batch_id, file_id, "validating")
        await websocket_manager.broadcast(batch_id, {
            "type": "file_update",
            "file_id": file_id,
            "status": "validating",
            "stage": "validation",
            "progress": 25
        })
        
        # Call validation service
        from app.services.business_card_validator import BusinessCardValidator
        validator = BusinessCardValidator()
        validation_result = await validator.validate_business_card(file_info["file_path"])
        
        # Broadcast validation result
        await websocket_manager.broadcast(batch_id, {
            "type": "validation_result",
            "file_id": file_id,
            "is_valid": validation_result["is_business_card"],
            "confidence": validation_result.get("confidence", "Unknown"),
            "reasoning": validation_result.get("reasoning", "")
        })
        
        if not validation_result["is_business_card"]:
            # Mark as failed, don't add to output queue
            queue_manager.update_input_status(batch_id, file_id, "invalid")
            await websocket_manager.broadcast(batch_id, {
                "type": "file_update",
                "file_id": file_id,
                "status": "invalid",
                "stage": "validation_failed",
                "progress": 100
            })
            return
        
        # Stage 3: Extraction (3-5s)
        queue_manager.update_input_status(batch_id, file_id, "extracting")
        await websocket_manager.broadcast(batch_id, {
            "type": "file_update",
            "file_id": file_id,
            "status": "extracting",
            "stage": "extraction",
            "progress": 50
        })
        
        # Call Gemini extraction
        from app.services.gemini_service import GeminiService
        gemini_service = GeminiService()
        extracted_records = await gemini_service.extract_document_data(file_info["file_path"])
        
        if not extracted_records or len(extracted_records) == 0:
            # Extraction failed
            queue_manager.update_input_status(batch_id, file_id, "extraction_failed")
            await websocket_manager.broadcast(batch_id, {
                "type": "file_update",
                "file_id": file_id,
                "status": "extraction_failed",
                "stage": "extraction_failed",
                "progress": 100
            })
            return
        
        # Stage 4: Processing data
        queue_manager.update_input_status(batch_id, file_id, "processing_data")
        await websocket_manager.broadcast(batch_id, {
            "type": "file_update",
            "file_id": file_id,
            "status": "processing_data",
            "stage": "processing_data",
            "progress": 75
        })
        
        # Clean and process extracted data
        processed_data = extracted_records[0]  # Take first record
        
        # Clean phone numbers
        if "phone" in processed_data and processed_data["phone"]:
            phone = processed_data["phone"]
            # Remove +91 if number is >10 digits and starts with 91
            if len(phone.replace(",", "").replace(" ", "")) > 10 and phone.startswith("91"):
                phone = phone[2:]
            processed_data["phone"] = phone
        
        # Stage 5: Completion
        processing_time = time.time() - start_time
        
        # Add to output queue with SAME file_id
        queue_manager.add_to_output_queue(batch_id, file_id, processed_data, processing_time)
        
        # Broadcast completion
        await websocket_manager.broadcast(batch_id, {
            "type": "extraction_complete",
            "file_id": file_id,
            "filename": file_info["filename"],
            "status": "completed",
            "stage": "completed",
            "progress": 100,
            "extracted_data": processed_data,
            "processing_time": processing_time
        })
        
        # Send batch summary update
        summary = queue_manager.get_batch_summary(batch_id)
        await websocket_manager.broadcast(batch_id, {
            "type": "batch_update",
            "batch_id": batch_id,
            "summary": summary
        })
        
    except Exception as e:
        # Handle errors
        queue_manager.update_input_status(batch_id, file_id, "failed")
        await websocket_manager.broadcast(batch_id, {
            "type": "error",
            "file_id": file_id,
            "error": str(e),
            "status": "failed"
        })

@router.get("/queue-status/{batch_id}")
async def get_queue_status(batch_id: str):
    """Get current queue status"""
    
    input_queue = queue_manager.get_input_queue(batch_id)
    output_queue = queue_manager.get_output_queue(batch_id)
    summary = queue_manager.get_batch_summary(batch_id)
    
    if not input_queue:
        raise HTTPException(status_code=404, detail="Batch not found")
    
    return {
        "batch_id": batch_id,
        "input_queue": input_queue,
        "output_queue": output_queue,
        "summary": summary
    }