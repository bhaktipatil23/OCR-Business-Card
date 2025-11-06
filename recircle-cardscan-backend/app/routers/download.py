from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from app.routers.process import processing_status
import os

router = APIRouter(prefix="/api/v1", tags=["download"])

@router.get("/download/{batch_id}")
async def download_csv(batch_id: str):
    """Download processed CSV file"""
    
    # Check if processing is completed
    if batch_id not in processing_status:
        raise HTTPException(status_code=404, detail="Batch not found")
    
    status_info = processing_status[batch_id]
    
    if status_info["status"] != "completed":
        raise HTTPException(status_code=400, detail="Processing not completed")
    
    csv_path = status_info.get("csv_path")
    
    if not csv_path or not os.path.exists(csv_path):
        raise HTTPException(status_code=404, detail="CSV file not found")
    
    return FileResponse(
        path=csv_path,
        media_type="text/csv",
        filename=f"{batch_id}_extracted_data.csv"
    )