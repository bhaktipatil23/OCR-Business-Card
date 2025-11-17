from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.services.database_service import DatabaseService
from pydantic import BaseModel
from typing import Optional
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1", tags=["field-updates"])

class FieldUpdateRequest(BaseModel):
    field: str
    value: str

class FieldUpdateResponse(BaseModel):
    success: bool
    message: str
    field: str
    old_value: Optional[str] = None
    new_value: str

@router.patch("/preview/{file_id}/update")
async def update_field(
    file_id: str,
    update_request: FieldUpdateRequest,
    db: Session = Depends(get_db)
):
    """Update a specific field for a business card and save edit history"""
    try:
        # Get current business card
        business_card = DatabaseService.get_business_card_by_file_id(db, file_id)
        if not business_card:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Business card not found"
            )
        
        # Get current value
        old_value = getattr(business_card, update_request.field, None) if hasattr(business_card, update_request.field) else None
        
        # Validate field name
        allowed_fields = ['name', 'phone', 'email', 'company', 'designation', 'address']
        if update_request.field not in allowed_fields:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Field '{update_request.field}' is not allowed. Allowed fields: {allowed_fields}"
            )
        
        # Save the edit
        success = DatabaseService.save_field_edit(
            db=db,
            file_id=file_id,
            field_name=update_request.field,
            old_value=old_value or "",
            new_value=update_request.value
        )
        
        if success:
            logger.info(f"Field '{update_request.field}' updated for file {file_id}: '{old_value}' -> '{update_request.value}'")
            return FieldUpdateResponse(
                success=True,
                message="Field updated successfully",
                field=update_request.field,
                old_value=old_value,
                new_value=update_request.value
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update field"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating field for file {file_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.get("/preview/{file_id}/edit-history")
async def get_edit_history(
    file_id: str,
    db: Session = Depends(get_db)
):
    """Get edit history for a business card"""
    try:
        edits = DatabaseService.get_edit_history(db, file_id)
        
        edit_history = []
        for edit in edits:
            edit_history.append({
                "id": edit.id,
                "field_name": edit.field_name,
                "old_value": edit.old_value,
                "new_value": edit.new_value,
                "edited_at": edit.edited_at.isoformat()
            })
        
        return {
            "file_id": file_id,
            "edit_history": edit_history,
            "total_edits": len(edit_history)
        }
        
    except Exception as e:
        logger.error(f"Error getting edit history for file {file_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )