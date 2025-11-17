from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.services.database_service import DatabaseService
from app.models.database import BusinessCard
from pydantic import BaseModel
from typing import List
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1", tags=["bulk-email"])

class BulkEmailRequest(BaseModel):
    emails: List[str]
    subject: str
    message: str

class EmailResult(BaseModel):
    email: str
    success: bool
    name: str = ""
    error: str = ""

@router.post("/send-bulk-email")
async def send_bulk_email(request: BulkEmailRequest, db: Session = Depends(get_db)):
    """Send emails to multiple recipients with auto-fetched names"""
    results = []
    
    for email in request.emails:
        try:
            # Fetch contact data from database
            business_card = db.query(BusinessCard).filter(
                BusinessCard.email == email,
                BusinessCard.is_valid_business_card == True
            ).first()
            
            name = business_card.name if business_card else "Dear Contact"
            
            # Here you would integrate with your email service (SMTP, SendGrid, etc.)
            # For now, we'll just simulate sending
            personalized_message = f"Dear {name},\n\n{request.message}"
            
            # Simulate email sending (replace with actual email service)
            email_sent = await simulate_send_email(email, request.subject, personalized_message)
            
            results.append(EmailResult(
                email=email,
                success=email_sent,
                name=name,
                error="" if email_sent else "Failed to send email"
            ))
            
        except Exception as e:
            logger.error(f"Error sending email to {email}: {e}")
            results.append(EmailResult(
                email=email,
                success=False,
                name="",
                error=str(e)
            ))
    
    return {
        "total_emails": len(request.emails),
        "successful": len([r for r in results if r.success]),
        "failed": len([r for r in results if not r.success]),
        "results": results
    }

async def simulate_send_email(email: str, subject: str, message: str) -> bool:
    """Simulate email sending - replace with actual email service"""
    # This is where you'd integrate with SMTP, SendGrid, AWS SES, etc.
    logger.info(f"Simulating email send to {email}: {subject}")
    return True  # Simulate success