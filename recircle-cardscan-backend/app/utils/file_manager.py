import os
import uuid
import aiofiles
from fastapi import UploadFile
from app.config import settings
from typing import Dict

class FileManager:
    
    @staticmethod
    def generate_file_id() -> str:
        """Generate unique file ID"""
        return f"f_{uuid.uuid4().hex[:8]}"
    
    @staticmethod
    def generate_batch_id() -> str:
        """Generate unique batch ID"""
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"batch_{timestamp}"
    
    @staticmethod
    async def save_uploaded_file(file: UploadFile, file_id: str) -> Dict:
        """Save uploaded file to storage"""
        # Create storage directory if not exists
        os.makedirs(settings.TEMP_STORAGE_PATH, exist_ok=True)
        
        # Generate safe filename
        file_extension = file.filename.split('.')[-1]
        safe_filename = f"{file_id}_{file.filename.replace('/', '_').replace('\\', '_')}"
        file_path = os.path.join(settings.TEMP_STORAGE_PATH, safe_filename)
        
        # Save file asynchronously
        async with aiofiles.open(file_path, 'wb') as out_file:
            content = await file.read()
            await out_file.write(content)
        
        return {
            "file_id": file_id,
            "filename": file.filename,
            "file_type": file.content_type,
            "size": len(content),
            "file_path": file_path
        }
    
    @staticmethod
    def cleanup_temp_files(batch_id: str) -> None:
        """Delete temporary files after processing"""
        # Implementation for cleanup
        pass