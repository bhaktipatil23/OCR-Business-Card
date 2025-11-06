from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from app.routers.process import processing_status
from app.core.data_store import data_store
from app.services.csv_writer import CSVWriter
import os

router = APIRouter(prefix="/api/v1", tags=["download"])

@router.get("/download/{batch_id}")
async def download_csv(batch_id: str):
    """Generate and download CSV file on-demand"""
    
    # Check if processing is completed
    if batch_id not in processing_status:
        raise HTTPException(status_code=404, detail="Batch not found")
    
    status_info = processing_status[batch_id]
    
    if status_info["status"] != "completed":
        raise HTTPException(status_code=400, detail="Processing not completed")
    
    # Get stored data
    records = data_store.get_batch_data(batch_id)
    
    if not records:
        raise HTTPException(status_code=404, detail="No extracted data found")
    
    # Generate CSV on-demand
    csv_writer = CSVWriter(batch_id)
    for record in records:
        csv_writer.write_record(record)
    
    csv_path = csv_writer.get_csv_path()
    
    if not os.path.exists(csv_path):
        raise HTTPException(status_code=500, detail="Failed to generate CSV")
    
    return FileResponse(
        path=csv_path,
        media_type="text/csv",
        filename=f"{batch_id}_extracted_data.csv"
    )