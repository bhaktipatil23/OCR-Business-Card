from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class ValidationResult(BaseModel):
    is_business_card: bool
    confidence: str
    reasoning: str
    information_found: List[str]
    raw_response: str

class FileInfo(BaseModel):
    file_id: str
    filename: str
    file_type: str
    size: int
    file_path: str
    validation: Optional[ValidationResult] = None

class UploadResponse(BaseModel):
    status: str
    batch_id: str
    uploaded_files: List[FileInfo]
    total_count: int
    message: str

class ExtractedData(BaseModel):
    file_id: str
    filename: str
    name: Optional[str] = "N/A"
    phone: Optional[str] = "N/A"
    email: Optional[str] = "N/A"
    company: Optional[str] = "N/A"
    designation: Optional[str] = "N/A"
    timestamp: str

class ProcessRequest(BaseModel):
    batch_id: str

class ProcessResponse(BaseModel):
    status: str
    batch_id: str
    total_files: int
    message: str

class StatusResponse(BaseModel):
    status: str
    batch_id: str
    progress: dict
    current_file: Optional[str] = None
    error: Optional[str] = None