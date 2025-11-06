from fastapi import APIRouter, HTTPException, BackgroundTasks
from app.models.schemas import ProcessRequest, ProcessResponse, StatusResponse
from app.core.processor import FileProcessor
from app.routers.upload import batch_storage, validation_storage
from app.utils.logger import app_logger

router = APIRouter(prefix="/api/v1", tags=["process"])

# Store processing status with thread-safe access
import threading
processing_status = {}
status_lock = threading.Lock()

async def background_processing(batch_id: str, files_list: list):
    """Background task for file processing with thread-safe status updates"""
    try:
        app_logger.info(f"[OCR] Processing {len(files_list)} files for batch {batch_id}")
        
        with status_lock:
            processing_status[batch_id] = {
                "status": "processing",
                "total_files": len(files_list),
                "processed": 0,
                "current_file": None
            }
        
        pass
        processor = FileProcessor(batch_id)
        
        pass
        result = await processor.process_all_files(files_list)
        
        app_logger.info(f"[OCR] Completed batch {batch_id}, CSV: {result.get('csv_path', 'N/A')}")
        
        with status_lock:
            processing_status[batch_id] = {
                "status": "completed",
                "total_files": len(files_list),
                "processed": len(files_list),
                "current_file": None,
                "csv_path": result["csv_path"]
            }
        
        app_logger.info(f"[OCR] Batch {batch_id} ready for download")
    except Exception as e:
        app_logger.error(f"[OCR] Failed batch {batch_id}: {str(e)}")
        import traceback
        traceback.print_exc()
        with status_lock:
            processing_status[batch_id] = {
                "status": "failed",
                "error": str(e),
                "total_files": len(files_list),
                "processed": 0
            }
        pass

@router.post("/process", response_model=ProcessResponse)
async def process_batch(
    request: ProcessRequest,
    background_tasks: BackgroundTasks
):
    """Start processing uploaded files"""
    
    batch_id = request.batch_id
    app_logger.info(f"[PROCESS] Starting processing for batch {batch_id}")
    
    # Check if batch exists
    if batch_id not in batch_storage:
        app_logger.error(f"[PROCESS] Batch not found: {batch_id}")
        raise HTTPException(status_code=404, detail="Batch not found")
    
    # Check if validation has been completed
    if batch_id not in validation_storage:
        app_logger.error(f"[PROCESS] Validation required for batch {batch_id}")
        raise HTTPException(status_code=400, detail="Files must be validated before processing")
    
    validation_results = validation_storage[batch_id]
    
    # Only process valid business cards
    valid_files = []
    invalid_files = []
    
    for file_info in batch_storage[batch_id]:
        # Check if file has validation result
        is_valid = False
        for valid_card in validation_results['valid_business_cards']:
            if valid_card['file_id'] == file_info['file_id']:
                valid_files.append(file_info)
                is_valid = True
                pass
                break
        
        if not is_valid:
            for invalid_file in validation_results['invalid_files']:
                if invalid_file['file_id'] == file_info['file_id']:
                    invalid_files.append(file_info)
                    pass
                    break
    
    if not valid_files:
        app_logger.error(f"[PROCESS] No valid business cards in batch {batch_id}")
        raise HTTPException(
            status_code=400, 
            detail=f"No valid business cards found. {len(invalid_files)} files are not business cards."
        )
    
    app_logger.info(f"[PROCESS] Processing {len(valid_files)} valid files, skipping {len(invalid_files)} invalid")
    
    # Start background processing with only valid files
    background_tasks.add_task(background_processing, batch_id, valid_files)
    
    app_logger.info(f"[PROCESS] OCR processing started for batch {batch_id}")
    
    return ProcessResponse(
        status="processing",
        batch_id=batch_id,
        total_files=len(valid_files),
        message=f"Processing started for {len(valid_files)} valid business cards. {len(invalid_files)} invalid files skipped."
    )

@router.get("/status/{batch_id}", response_model=StatusResponse)
async def get_status(batch_id: str):
    """Get processing status with thread-safe access"""
    
    with status_lock:
        if batch_id not in processing_status:
            raise HTTPException(status_code=404, detail="Status not found")
        
        status_info = processing_status[batch_id].copy()  # Create a copy to avoid race conditions
    
    # Handle failed status
    if status_info["status"] == "failed":
        return StatusResponse(
            status="failed",
            batch_id=batch_id,
            progress={
                "total_files": status_info.get("total_files", 0),
                "processed": status_info.get("processed", 0),
                "percentage": 0
            },
            current_file=None,
            error=status_info.get("error", "Unknown error")
        )
    
    return StatusResponse(
        status=status_info["status"],
        batch_id=batch_id,
        progress={
            "total_files": status_info.get("total_files", 0),
            "processed": status_info.get("processed", 0),
            "percentage": int((status_info.get("processed", 0) / status_info.get("total_files", 1)) * 100)
        },
        current_file=status_info.get("current_file")
    )