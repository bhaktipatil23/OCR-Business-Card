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

# Store individual file status and queue
file_status = {}
file_queue = {}
file_lock = threading.Lock()



import asyncio

async def background_processing(batch_id: str, files_list: list):
    """Background task for file processing with thread-safe status updates"""
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()
    
    # No need for SQLAlchemy session anymore
    db = None
    
    try:
        app_logger.info(f"[OCR] Processing {len(files_list)} files for batch {batch_id}")
        
        with status_lock:
            processing_status[batch_id] = {
                "status": "processing",
                "total_files": len(files_list),
                "processed": 0,
                "current_file": None
            }
        
        processor = FileProcessor(batch_id)
        
        result = await processor.process_all_files(files_list)
        
        # Database saving removed - data only stored in memory for CSV export
        
        # Skip batch status update for simplified schema
        
        app_logger.info(f"[OCR] Completed batch {batch_id}, Records: {result.get('records_count', 0)}")
        
        with status_lock:
            processing_status[batch_id] = {
                "status": "completed",
                "total_files": len(files_list),
                "processed": len(files_list),
                "current_file": None,
                "records_count": result.get("records_count", 0),
                "extracted_data": result.get("extracted_data", [])
            }
        
        app_logger.info(f"[OCR] Batch {batch_id} ready for download")
    except Exception as e:
        app_logger.error(f"[OCR] Failed batch {batch_id}: {str(e)}")
        import traceback
        traceback.print_exc()
        # Skip batch status update for simplified schema
        
        with status_lock:
            processing_status[batch_id] = {
                "status": "failed",
                "error": str(e),
                "total_files": len(files_list),
                "processed": 0
            }
    finally:
        # No database session to close
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
    
    # Skip batch status update for simplified schema
    
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

@router.get("/extracted-data/{batch_id}")
async def get_extracted_data(batch_id: str):
    """Get all extracted data for a completed batch"""
    
    with status_lock:
        if batch_id not in processing_status:
            raise HTTPException(status_code=404, detail="Batch not found")
        
        status_info = processing_status[batch_id]
        if status_info["status"] != "completed":
            raise HTTPException(status_code=400, detail=f"Batch is not completed. Current status: {status_info['status']}")
    
    # Get extracted data from data store
    from app.core.data_store import data_store
    extracted_data = data_store.get_batch_data(batch_id)
    
    if not extracted_data:
        raise HTTPException(status_code=404, detail="No extracted data found for this batch")
    
    return {
        "status": "success",
        "batch_id": batch_id,
        "total_records": len(extracted_data),
        "extracted_data": extracted_data
    }

@router.get("/file-status/{batch_id}")
async def get_file_status(batch_id: str):
    """Get individual file processing status"""
    
    with file_lock:
        if batch_id not in file_status:
            raise HTTPException(status_code=404, detail="Batch not found")
        
        return {
            "batch_id": batch_id,
            "files": file_status[batch_id],
            "queue_data": file_queue.get(batch_id, [])
        }

@router.get("/saved-data/{batch_id}")
async def get_saved_data(batch_id: str):
    """Get saved extracted data from database"""
    try:
        import mysql.connector
        import os
        
        conn = mysql.connector.connect(
            host=os.getenv('DB_HOST', 'localhost'),
            port=int(os.getenv('DB_PORT', 3306)),
            user=os.getenv('DB_USER', 'root'),
            password=os.getenv('DB_PASSWORD', 'NewPassword123!'),
            database=os.getenv('DB_NAME', 'business_card_ocr')
        )
        cursor = conn.cursor(dictionary=True)
        
        # Get only the most recent unique business cards data
        query = """
        SELECT name, phone, email, company, designation, address
        FROM business_cards 
        WHERE batch_id = %s
        ORDER BY id DESC
        """
        cursor.execute(query, (batch_id,))
        cards_data = cursor.fetchall()
        
        # Remove duplicates based on phone number (assuming phone is unique identifier)
        seen_phones = set()
        unique_cards = []
        for card in cards_data:
            if card['phone'] not in seen_phones:
                unique_cards.append(card)
                seen_phones.add(card['phone'])
        
        cards_data = unique_cards
        
        cursor.close()
        conn.close()
        
        if not cards_data:
            raise HTTPException(status_code=404, detail="No saved data found for this batch")
        
        return {
            "status": "success",
            "batch_id": batch_id,
            "total_records": len(cards_data),
            "extracted_data": cards_data
        }
        
    except mysql.connector.Error as db_error:
        print(f"[SAVED-DATA] Database error: {str(db_error)}")
        raise HTTPException(status_code=500, detail=f"Database error: {str(db_error)}")
    except Exception as e:
        print(f"[SAVED-DATA] General error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@router.get("/recent-batches")
async def get_recent_batches():
    """Get recent batch IDs for data recovery"""
    try:
        import mysql.connector
        import os
        
        conn = mysql.connector.connect(
            host=os.getenv('DB_HOST', 'localhost'),
            port=int(os.getenv('DB_PORT', 3306)),
            user=os.getenv('DB_USER', 'root'),
            password=os.getenv('DB_PASSWORD', 'NewPassword123!'),
            database=os.getenv('DB_NAME', 'business_card_ocr')
        )
        cursor = conn.cursor(dictionary=True)
        
        # Get only the most recent saved batch
        query = """
        SELECT batch_id, name, team, event
        FROM events 
        ORDER BY id DESC 
        LIMIT 1
        """
        cursor.execute(query)
        batches = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        return {
            "status": "success",
            "batches": batches
        }
        
    except mysql.connector.Error as db_error:
        print(f"[RECENT-BATCHES] Database error: {str(db_error)}")
        raise HTTPException(status_code=500, detail=f"Database error: {str(db_error)}")
    except Exception as e:
        print(f"[RECENT-BATCHES] General error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@router.post("/start-individual-processing")
async def start_individual_processing(
    request: ProcessRequest,
    background_tasks: BackgroundTasks
):
    """Start individual file processing with queue updates"""
    
    batch_id = request.batch_id
    
    if batch_id not in batch_storage:
        raise HTTPException(status_code=404, detail="Batch not found")
    
    if batch_id not in validation_storage:
        raise HTTPException(status_code=400, detail="Files must be validated first")
    
    # Initialize file status
    with file_lock:
        file_status[batch_id] = {}
        file_queue[batch_id] = []
        
        for file_info in batch_storage[batch_id]:
            file_status[batch_id][file_info['file_id']] = {
                "filename": file_info['filename'],
                "status": "pending",
                "validation": None,
                "extracted_data": None
            }
    
    # Start individual processing
    background_tasks.add_task(process_files_individually, batch_id)
    
    return {
        "status": "started",
        "batch_id": batch_id,
        "message": "Individual file processing started"
    }

async def process_files_individually(batch_id: str):
    """Process files one by one and update queue with WebSocket updates"""
    
    try:
        from app.services.websocket_manager import websocket_manager
        validation_results = validation_storage[batch_id]
        
        for file_info in batch_storage[batch_id]:
            file_id = file_info['file_id']
            
            # Update to validating
            with file_lock:
                file_status[batch_id][file_id]["status"] = "validating"
            
            # WebSocket update - validation started
            await websocket_manager.broadcast(batch_id, {
                "type": "file_update",
                "file_id": file_id,
                "filename": file_info['filename'],
                "status": "validating",
                "progress": 25
            })
            
            app_logger.info(f"[VALIDATION] Starting validation for {file_info['filename']}")
            await asyncio.sleep(2.0)  # Longer validation time for visibility
            
            # Check validation result
            is_valid = False
            validation_result = None
            
            for valid_card in validation_results['valid_business_cards']:
                if valid_card['file_id'] == file_id:
                    is_valid = True
                    validation_result = valid_card['validation']
                    break
            
            if not is_valid:
                for invalid_file in validation_results['invalid_files']:
                    if invalid_file['file_id'] == file_id:
                        validation_result = invalid_file['validation']
                        break
            
            with file_lock:
                file_status[batch_id][file_id]["validation"] = validation_result
            
            # WebSocket update - validation result
            await websocket_manager.broadcast(batch_id, {
                "type": "validation_result",
                "file_id": file_id,
                "filename": file_info['filename'],
                "is_valid": is_valid,
                "reasoning": validation_result.get('reasoning', '') if validation_result else ''
            })
            
            app_logger.info(f"[VALIDATION] {file_info['filename']} validation result: {'VALID' if is_valid else 'INVALID'}")
            await asyncio.sleep(1.0)  # Pause after validation
            
            if is_valid:
                # Update to processing
                with file_lock:
                    file_status[batch_id][file_id]["status"] = "processing"
                
                # WebSocket update - extraction started
                await websocket_manager.broadcast(batch_id, {
                    "type": "file_update",
                    "file_id": file_id,
                    "filename": file_info['filename'],
                    "status": "extracting",
                    "progress": 50
                })
                
                app_logger.info(f"[PROCESSING] Starting OCR extraction for {file_info['filename']}")
                
                # Real OCR extraction using Gemini service
                try:
                    from app.services.gemini_service import GeminiService
                    gemini_service = GeminiService()
                    
                    # Extract data from the actual file
                    extracted_records = await gemini_service.extract_document_data(file_info['file_path'])
                    
                    if extracted_records and len(extracted_records) > 0:
                        # Process ALL extracted records from the image
                        cards_added = 0
                        with file_lock:
                            file_status[batch_id][file_id]["status"] = "completed"
                            file_status[batch_id][file_id]["extracted_data"] = extracted_records
                            
                            # Add each business card to queue
                            for card_index, extracted_data in enumerate(extracted_records):
                                file_queue[batch_id].append({
                                    "file_id": f"{file_id}_card_{card_index + 1}",
                                    "filename": f"{file_info['filename']} (Card {card_index + 1})",
                                    "name": extracted_data.get("name", "N/A"),
                                    "phone": extracted_data.get("phone", "N/A"),
                                    "email": extracted_data.get("email", "N/A"),
                                    "company": extracted_data.get("company", "N/A"),
                                    "designation": extracted_data.get("designation", "N/A"),
                                    "address": extracted_data.get("address", "N/A")
                                })
                                cards_added += 1
                        
                        # WebSocket update - extraction complete
                        await websocket_manager.broadcast(batch_id, {
                            "type": "extraction_complete",
                            "file_id": file_id,
                            "filename": file_info['filename'],
                            "status": "completed",
                            "progress": 100,
                            "extracted_data": extracted_records[0] if extracted_records else {},
                            "cards_count": cards_added
                        })
                        
                        app_logger.info(f"[COMPLETED] {file_info['filename']} processed successfully - {cards_added} cards extracted")
                    else:
                        # No data extracted
                        with file_lock:
                            file_status[batch_id][file_id]["status"] = "completed"
                            file_status[batch_id][file_id]["extracted_data"] = None
                        
                        app_logger.info(f"[COMPLETED] {file_info['filename']} processed but no business cards found")
                        
                except Exception as extract_error:
                    app_logger.error(f"[ERROR] Extraction failed for {file_info['filename']}: {str(extract_error)}")
                    with file_lock:
                        file_status[batch_id][file_id]["status"] = "error"
            else:
                # Update to invalid
                with file_lock:
                    file_status[batch_id][file_id]["status"] = "invalid"
                
                # WebSocket update - invalid file
                await websocket_manager.broadcast(batch_id, {
                    "type": "file_update",
                    "file_id": file_id,
                    "filename": file_info['filename'],
                    "status": "invalid",
                    "progress": 100
                })
                
                app_logger.info(f"[INVALID] {file_info['filename']} marked as invalid business card")
        
        # Mark batch as completed
        with status_lock:
            processing_status[batch_id] = {
                "status": "completed",
                "total_files": len(batch_storage[batch_id]),
                "processed": len([f for f in file_status[batch_id].values() if f["status"] in ["completed", "invalid"]]),
                "queue_size": len(file_queue[batch_id])
            }
        
        # Store in data store for CSV export
        from app.core.data_store import data_store
        data_store.store_batch_data(batch_id, file_queue[batch_id])
        
        # WebSocket update - batch complete
        await websocket_manager.broadcast(batch_id, {
            "type": "batch_complete",
            "batch_id": batch_id,
            "total_files": len(batch_storage[batch_id]),
            "completed_files": len([f for f in file_status[batch_id].values() if f["status"] == "completed"]),
            "total_records": len(file_queue[batch_id]),
            "download_url": f"/api/v1/download/{batch_id}"
        })
        
        app_logger.info(f"[QUEUE] Batch {batch_id} completed with {len(file_queue[batch_id])} records in queue")
        
    except Exception as e:
        app_logger.error(f"[QUEUE] Error processing batch {batch_id}: {str(e)}")
        with status_lock:
            processing_status[batch_id] = {
                "status": "failed",
                "error": str(e)
            }

