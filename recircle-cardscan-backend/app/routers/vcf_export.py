from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from app.services.vcf_converter import VCFConverter
from app.config import settings
import os
import glob

router = APIRouter()

@router.get("/export-vcf/{batch_id}")
async def export_to_vcf(batch_id: str):
    """Convert CSV to VCF and download"""
    try:
        # Find the CSV file for this batch
        csv_pattern = os.path.join(settings.OUTPUT_CSV_PATH, f"{batch_id}_data.csv")
        
        if not os.path.exists(csv_pattern):
            raise HTTPException(status_code=404, detail="CSV file not found")
        
        # Convert CSV to VCF
        vcf_converter = VCFConverter(batch_id)
        vcf_file_path = vcf_converter.csv_to_vcf(csv_pattern)
        
        # Return VCF file for download
        return FileResponse(
            path=vcf_file_path,
            filename=f"{batch_id}_contacts.vcf",
            media_type="text/vcard"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"VCF export failed: {str(e)}")

@router.get("/vcf-url/{batch_id}")
async def get_vcf_download_url(batch_id: str):
    """Get VCF download URL"""
    return {
        "vcf_url": f"/api/v1/export-vcf/{batch_id}",
        "filename": f"{batch_id}_contacts.vcf"
    }