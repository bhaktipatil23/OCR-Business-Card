from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
import os
import json
import glob

router = APIRouter()

@router.get("/test")
async def test_endpoint():
    """Simple test endpoint"""
    return {"message": "API is working", "status": "success"}

class UpdateFieldRequest(BaseModel):
    field: str
    value: str

# Simple in-memory storage
data_store = {}

@router.get("/preview/{file_id}")
async def get_document_preview(file_id: str):
    """Get document preview with actual extracted data"""
    try:
        from app.config import settings
        from app.services.gemini_service import GeminiService
        import glob
        
        # Find the actual uploaded file
        file_patterns = [
            os.path.join(settings.TEMP_STORAGE_PATH, f"{file_id}.*"),
            os.path.join(settings.TEMP_STORAGE_PATH, f"*{file_id}*")
        ]
        
        found_file = None
        for pattern in file_patterns:
            matches = glob.glob(pattern)
            if matches:
                found_file = matches[0]
                break
        
        if found_file and os.path.exists(found_file):
            # Extract actual data from the file
            gemini_service = GeminiService()
            filename = os.path.basename(found_file)
            
            # Detect document type
            document_type = "business_card"
            if any(keyword in filename.lower() for keyword in ['challan', 'invoice', 'receipt', 'transport']):
                document_type = "delivery_challan"
            
            # Handle PDF conversion if needed
            processing_file = found_file
            if found_file.lower().endswith('.pdf'):
                from app.services.pdf_converter import PDFConverter
                pdf_converter = PDFConverter()
                images = pdf_converter.convert_pdf_to_images(found_file)
                if images:
                    temp_image_path = found_file.replace('.pdf', '_temp.jpg')
                    images[0].save(temp_image_path)
                    processing_file = temp_image_path
            
            # Extract data using Gemini (this returns records with multiple phone entries)
            extracted_records = await gemini_service.extract_document_data(processing_file, document_type)
            
            if extracted_records and len(extracted_records) > 0:
                # Group records by business card (consolidate phone number rows)
                consolidated_records = _consolidate_phone_records(extracted_records)
                
                response_data = {
                    "filename": filename,
                    "page": 1,
                    "document_type": document_type,
                    "total_records": len(consolidated_records),
                    "records": []
                }
                
                # Process each consolidated record
                for i, consolidated_data in enumerate(consolidated_records):
                    record = {
                        "record_id": i + 1,
                        "data": consolidated_data
                    }
                    
                    # Apply any manual updates for this specific record
                    record_key = f"{file_id}_{i}"
                    if record_key in data_store:
                        record["data"].update(data_store[record_key])
                    
                    response_data["records"].append(record)
                
                return response_data
            else:
                raise HTTPException(status_code=500, detail="No data could be extracted from the file")
        
        # File not found - return error
        raise HTTPException(status_code=404, detail="File not found or not processed yet")
        
    except Exception as e:
        print(f"Error in preview: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to extract data: {str(e)}")

@router.patch("/preview/{file_id}/update")
async def update_document_field(file_id: str, request: UpdateFieldRequest):
    """Update a field in the document"""
    try:
        if file_id not in data_store:
            data_store[file_id] = {}
        
        data_store[file_id][request.field] = request.value
        
        return {"success": True, "message": "Field updated"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/preview/{file_id}/image")
async def get_document_image(file_id: str):
    """Get actual document image"""
    try:
        from app.config import settings
        import glob
        
        # Find the actual uploaded file
        file_patterns = [
            os.path.join(settings.TEMP_STORAGE_PATH, f"{file_id}.*"),
            os.path.join(settings.TEMP_STORAGE_PATH, f"*{file_id}*")
        ]
        
        found_file = None
        for pattern in file_patterns:
            matches = glob.glob(pattern)
            if matches:
                found_file = matches[0]
                break
        
        if found_file and os.path.exists(found_file):
            # If it's a PDF, convert to image
            if found_file.lower().endswith('.pdf'):
                from app.services.pdf_converter import PDFConverter
                pdf_converter = PDFConverter()
                images = pdf_converter.convert_pdf_to_images(found_file)
                if images:
                    temp_image_path = found_file.replace('.pdf', '_preview.jpg')
                    images[0].save(temp_image_path)
                    return FileResponse(temp_image_path)
            else:
                # Return image file directly
                return FileResponse(found_file)
        
        # Fallback to SVG placeholder
        from fastapi.responses import Response
        doc_type = "Business Card" if "card" in file_id.lower() else "Document"
        
        svg_content = f"""
        <svg width="400" height="300" xmlns="http://www.w3.org/2000/svg">
            <rect width="400" height="300" fill="#f8f9fa" stroke="#dee2e6" stroke-width="2"/>
            <text x="200" y="150" text-anchor="middle" font-family="Arial" font-size="16" fill="#495057">
                {doc_type} Image Not Found
            </text>
            <text x="200" y="180" text-anchor="middle" font-family="Arial" font-size="12" fill="#868e96">
                File ID: {file_id}
            </text>
        </svg>
        """
        
        return Response(content=svg_content, media_type="image/svg+xml")
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def _consolidate_phone_records(extracted_records):
    """Consolidate multiple phone number records into single business card records"""
    consolidated = []
    current_card = None
    
    for record in extracted_records:
        # Check if this is a main record (has name/company) or additional phone record
        has_main_data = (
            record.get('name') and record.get('name') != '' and record.get('name') != 'N/A'
        ) or (
            record.get('company') and record.get('company') != '' and record.get('company') != 'N/A'
        )
        
        if has_main_data:
            # This is a new business card
            current_card = record.copy()
            # Collect all phone numbers for this card
            phones = []
            if record.get('phone') and record.get('phone') != 'N/A':
                phones.append(record.get('phone'))
            
            # Look ahead for additional phone numbers
            for next_record in extracted_records[extracted_records.index(record) + 1:]:
                # If next record has no main data but has phone, it's additional phone for current card
                if (not next_record.get('name') or next_record.get('name') == '') and \
                   (not next_record.get('company') or next_record.get('company') == '') and \
                   next_record.get('phone') and next_record.get('phone') != 'N/A':
                    phones.append(next_record.get('phone'))
                else:
                    break
            
            # Combine all phone numbers
            if len(phones) > 1:
                current_card['phone'] = ','.join(phones)
            
            consolidated.append(current_card)
    
    return consolidated

@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "pdf_preview"}

