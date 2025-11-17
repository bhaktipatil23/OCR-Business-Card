from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.database import BusinessCard
from pydantic import BaseModel
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1", tags=["category-email"])

class EventEmailRequest(BaseModel):
    event_names: List[str]  # e.g., ['Tech Conference 2024', 'Business Summit']
    event_types: List[str]  # e.g., ['Conference', 'Workshop']
    subject: str
    message: str
    company_filter: Optional[str] = None  # Optional company filter

@router.get("/events")
async def get_events(db: Session = Depends(get_db)):
    """Get all available event names and types from business cards"""
    try:
        event_names = db.query(BusinessCard.event_name).filter(
            BusinessCard.event_name.isnot(None),
            BusinessCard.is_valid_business_card == True
        ).distinct().all()
        
        event_types = db.query(BusinessCard.event_type).filter(
            BusinessCard.event_type.isnot(None),
            BusinessCard.is_valid_business_card == True
        ).distinct().all()
        
        return {
            "event_names": [name[0] for name in event_names if name[0]],
            "event_types": [type_[0] for type_ in event_types if type_[0]]
        }
        
    except Exception as e:
        logger.error(f"Error fetching categories: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/send-event-email")
async def send_event_email(request: EventEmailRequest, db: Session = Depends(get_db)):
    """Send emails to contacts by event name and type"""
    try:
        # Build query with OR condition for event names and types
        query = db.query(BusinessCard).filter(
            BusinessCard.email.isnot(None),
            BusinessCard.is_valid_business_card == True
        )
        
        # Add event filters
        event_filters = []
        if request.event_names:
            event_filters.append(BusinessCard.event_name.in_(request.event_names))
        if request.event_types:
            event_filters.append(BusinessCard.event_type.in_(request.event_types))
        
        if event_filters:
            from sqlalchemy import or_
            query = query.filter(or_(*event_filters))
        
        # Add company filter if provided
        if request.company_filter:
            query = query.filter(BusinessCard.company.ilike(f"%{request.company_filter}%"))
        
        contacts = query.all()
        
        results = []
        for contact in contacts:
            try:
                name = contact.name or "Dear Contact"
                personalized_message = f"Dear {name},\n\n{request.message}"
                
                # Simulate email sending
                email_sent = await simulate_send_email(contact.email, request.subject, personalized_message)
                
                results.append({
                    "email": contact.email,
                    "name": name,
                    "event_name": contact.event_name,
                    "event_type": contact.event_type,
                    "company": contact.company,
                    "success": email_sent,
                    "error": "" if email_sent else "Failed to send email"
                })
                
            except Exception as e:
                logger.error(f"Error sending email to {contact.email}: {e}")
                results.append({
                    "email": contact.email,
                    "name": contact.name or "",
                    "event_name": contact.event_name,
                    "event_type": contact.event_type,
                    "company": contact.company,
                    "success": False,
                    "error": str(e)
                })
        
        return {
            "total_contacts": len(contacts),
            "successful": len([r for r in results if r["success"]]),
            "failed": len([r for r in results if not r["success"]]),
            "event_names_used": request.event_names,
            "event_types_used": request.event_types,
            "company_filter": request.company_filter,
            "results": results
        }
        
    except Exception as e:
        logger.error(f"Error in category email sending: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

async def simulate_send_email(email: str, subject: str, message: str) -> bool:
    """Simulate email sending"""
    logger.info(f"Sending event email to {email}: {subject}")
    return True