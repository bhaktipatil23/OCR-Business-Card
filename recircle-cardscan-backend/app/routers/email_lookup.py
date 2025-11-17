from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.database import BusinessCard
from typing import Optional
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1", tags=["email-lookup"])

@router.get("/lookup/email/{email}")
async def lookup_by_email(email: str, db: Session = Depends(get_db)):
    """Lookup business card data by email address"""
    try:
        # Search for business card with matching email
        business_card = db.query(BusinessCard).filter(
            BusinessCard.email == email,
            BusinessCard.is_valid_business_card == True
        ).first()
        
        if business_card:
            return {
                "found": True,
                "data": {
                    "name": business_card.name,
                    "phone": business_card.phone,
                    "company": business_card.company,
                    "designation": business_card.designation,
                    "address": business_card.address
                }
            }
        else:
            return {"found": False, "data": None}
            
    except Exception as e:
        logger.error(f"Error looking up email {email}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")