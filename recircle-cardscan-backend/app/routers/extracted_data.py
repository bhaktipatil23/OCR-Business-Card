from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any
from app.core.data_store import data_store

router = APIRouter(prefix="/api/v1", tags=["extracted-data"])

@router.get("/extracted-data/{batch_id}")
async def get_extracted_data(batch_id: str):
    """Get extracted data for a batch from memory"""
    try:
        # Get data from memory store
        records = data_store.get_batch_data(batch_id)
        
        if not records:
            raise HTTPException(status_code=404, detail="No extracted data found for this batch")
        
        # Group by file_id and convert to required format
        result = []
        file_groups = {}
        
        for record in records:
            file_id = record.get('file_id')
            if file_id not in file_groups:
                file_groups[file_id] = {
                    "file_id": file_id,
                    "filename": record.get('filename', 'unknown'),
                    "extracted_data": []
                }
            
            file_groups[file_id]["extracted_data"].append({
                "name": record.get('name', 'N/A'),
                "phone": record.get('phone', 'N/A'),
                "email": record.get('email', 'N/A'),
                "company": record.get('company', 'N/A'),
                "designation": record.get('designation', 'N/A'),
                "address": record.get('address', 'N/A')
            })
        
        result = list(file_groups.values())
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading extracted data: {str(e)}")