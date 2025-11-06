from fastapi import UploadFile, HTTPException
from app.config import settings
from typing import List

class FileValidator:
    
    @staticmethod
    def validate_file_extension(filename: str) -> bool:
        """Check if file extension is allowed"""
        ext = filename.split('.')[-1].lower()
        return ext in settings.allowed_extensions_list
    
    @staticmethod
    async def validate_file_size(file: UploadFile, max_size_mb: int = 20) -> bool:
        """Check if individual file size is within limit (20MB default)"""
        max_size_bytes = max_size_mb * 1024 * 1024
        
        # Get current position
        current_pos = file.file.tell() if hasattr(file.file, 'tell') else 0
        
        # Read content to get size
        content = await file.read()
        file_size = len(content)
        
        # Reset file position
        await file.seek(current_pos)
        
        return file_size <= max_size_bytes
    
    @staticmethod
    async def validate_batch_size(files: List[UploadFile]) -> None:
        """Check if number of files and total batch size exceeds limits"""
        from app.utils.logger import app_logger
        
        # Check file count limit
        if len(files) > settings.MAX_FILES_PER_BATCH:
            error_msg = f"Maximum {settings.MAX_FILES_PER_BATCH} files allowed, got {len(files)}"
            app_logger.error(f"[UPLOAD] {error_msg}")
            raise HTTPException(status_code=400, detail=error_msg)
        
        # Check total batch size (20MB limit)
        max_batch_size_bytes = 20 * 1024 * 1024  # 20MB
        total_size = 0
        
        for file in files:
            content = await file.read()
            total_size += len(content)
            await file.seek(0)  # Reset file pointer
        
        total_size_mb = total_size / (1024 * 1024)
        
        if total_size > max_batch_size_bytes:
            error_msg = f"Total batch size {total_size_mb:.1f}MB exceeds 20MB limit"
            app_logger.error(f"[UPLOAD] {error_msg}")
            raise HTTPException(status_code=400, detail=error_msg)
        
        app_logger.info(f"[UPLOAD] Batch validation passed: {len(files)} files, {total_size_mb:.1f}MB total")