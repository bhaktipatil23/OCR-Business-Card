from fastapi import APIRouter, UploadFile, File, HTTPException
from typing import List
from app.models.schemas import UploadResponse, FileInfo, ValidationResult
from app.utils.file_validator import FileValidator
from app.utils.file_manager import FileManager
from app.services.business_card_validator import BusinessCardValidator
from app.utils.logger import app_logger

router = APIRouter(prefix="/api/v1", tags=["upload"])

# In-memory storage for batch files
batch_storage = {}
# Storage for validation results
validation_storage = {}

@router.post("/upload", response_model=UploadResponse)
async def upload_files(files: List[UploadFile] = File(...)):
    """Upload multiple files (max 100)"""
    
    try:
        app_logger.info(f"[UPLOAD] Starting upload: {len(files)} files")
        
        # Validate batch size and total size
        await FileValidator.validate_batch_size(files)
        app_logger.info(f"[UPLOAD] Batch validation passed")
    except HTTPException as e:
        app_logger.error(f"[UPLOAD] Batch validation failed: {str(e.detail)}")
        raise
    except Exception as e:
        app_logger.error(f"[UPLOAD] Unexpected error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    
    # Generate batch ID
    batch_id = FileManager.generate_batch_id()
    app_logger.info(f"[UPLOAD] Batch ID: {batch_id}")
    uploaded_files = []
    
    # Skip database batch creation
    
    for file in files:
        # Validate file extension
        if not FileValidator.validate_file_extension(file.filename):
            app_logger.error(f"[UPLOAD] Invalid file type: {file.filename}")
            raise HTTPException(
                status_code=400,
                detail=f"Invalid file type: {file.filename}"
            )
        
        # Generate unique file ID
        file_id = FileManager.generate_file_id()
        
        # Save file
        file_info = await FileManager.save_uploaded_file(file, file_id)
        uploaded_files.append(file_info)
        
        # Skip database record creation
    
    # Store in memory
    batch_storage[batch_id] = uploaded_files
    app_logger.info(f"[UPLOAD] Completed: {len(uploaded_files)} files uploaded")
    
    return UploadResponse(
        status="success",
        batch_id=batch_id,
        uploaded_files=[FileInfo(**f) for f in uploaded_files],
        total_count=len(uploaded_files),
        message="Files uploaded successfully. Please validate before processing."
    )

@router.post("/validate/{batch_id}")
async def validate_batch(batch_id: str):
    """Validate uploaded files for business card detection"""
    
    app_logger.info(f"[VALIDATION] Starting validation for batch {batch_id}")
    
    # Check if batch exists
    if batch_id not in batch_storage:
        app_logger.error(f"[VALIDATION] Batch not found: {batch_id}")
        raise HTTPException(status_code=404, detail="Batch not found")
    
    files_list = batch_storage[batch_id]
    files_list = batch_storage[batch_id]
    
    # Initialize validator
    validator = BusinessCardValidator()
    
    # Validate all files
    validation_results = await validator.validate_batch(files_list)
    
    # Store validation results
    validation_storage[batch_id] = validation_results
    
    # Log validation summary
    valid_count = validation_results['validation_summary']['valid_cards']
    invalid_count = validation_results['validation_summary']['invalid_files']
    app_logger.info(f"[VALIDATION] Results: {valid_count} valid, {invalid_count} invalid")
    
    # Update file info with validation results and save to database
    for file_info in files_list:
        validation_result = None
        
        # Find validation result for this file
        for valid_card in validation_results['valid_business_cards']:
            if valid_card['file_id'] == file_info['file_id']:
                validation_result = ValidationResult(**valid_card['validation'])
                file_info['validation'] = validation_result
                break
        
        for invalid_file in validation_results['invalid_files']:
            if invalid_file['file_id'] == file_info['file_id']:
                validation_result = ValidationResult(**invalid_file['validation'])
                file_info['validation'] = validation_result
                break
        
        # Skip database validation update
    
    # Skip batch status update
    
    app_logger.info(f"[VALIDATION] Completed validation for batch {batch_id}")
    
    return {
        "status": "validation_completed",
        "batch_id": batch_id,
        "validation_summary": validation_results['validation_summary'],
        "valid_business_cards": len(validation_results['valid_business_cards']),
        "invalid_files": len(validation_results['invalid_files']),
        "message": f"Validation completed. {validation_results['validation_summary']['valid_cards']} business cards found, {validation_results['validation_summary']['invalid_files']} invalid files."
    }

@router.get("/validation-status/{batch_id}")
async def get_validation_status(batch_id: str):
    """Get validation results for a batch"""
    
    app_logger.info(f"[VALIDATION-STATUS] Checking status for batch {batch_id}")
    app_logger.info(f"[VALIDATION-STATUS] Available batches: {list(validation_storage.keys())}")
    
    if batch_id not in validation_storage:
        app_logger.error(f"[VALIDATION-STATUS] Batch not found: {batch_id}")
        raise HTTPException(status_code=404, detail=f"Validation results not found for batch {batch_id}")
    
    app_logger.info(f"[VALIDATION-STATUS] Returning results for batch {batch_id}")
    return validation_storage[batch_id]