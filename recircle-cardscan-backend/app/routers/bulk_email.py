from fastapi import APIRouter, HTTPException
from app.services.email_service import email_service
from app.config import settings
from pydantic import BaseModel
from typing import List
import logging
import mysql.connector

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
async def send_bulk_email(request: BulkEmailRequest):
    """Send emails to multiple recipients with auto-fetched names"""
    results = []

    # Try to get names from database
    email_to_name = {}
    try:
        conn = mysql.connector.connect(
            host=settings.DB_HOST,
            port=settings.DB_PORT,
            user=settings.DB_USER,
            password=settings.DB_PASSWORD,
            database=settings.DB_NAME
        )
        cursor = conn.cursor(dictionary=True)

        # Fetch names for all emails
        if request.emails:
            placeholders = ', '.join(['%s'] * len(request.emails))
            query = f"""
                SELECT DISTINCT email, name
                FROM business_cards
                WHERE email IN ({placeholders})
            """
            cursor.execute(query, tuple(request.emails))
            rows = cursor.fetchall()

            for row in rows:
                if row['email'] and row['name']:
                    email_to_name[row['email']] = row['name']

        cursor.close()
        conn.close()
        logger.info(f"Fetched {len(email_to_name)} names from database")

    except Exception as db_error:
        logger.warning(f"Could not fetch names from database: {db_error}")
        # Continue without names

    # Send emails
    for email in request.emails:
        try:
            name = email_to_name.get(email, "Contact")

            # Personalize message by replacing placeholders
            personalized_message = request.message

            # Replace common placeholders
            personalized_message = personalized_message.replace("{{name}}", name)
            personalized_message = personalized_message.replace("{{Name}}", name)
            personalized_message = personalized_message.replace("{{NAME}}", name.upper())
            personalized_message = personalized_message.replace("{{email}}", email)

            # Also replace generic greetings if no name in database
            if name == "Contact":
                personalized_message = personalized_message.replace("Dear Contact,", "Dear Business Partner,")

            # Send email using real SMTP service
            logger.info(f"Sending email to {email} (name: {name})")
            email_sent = await email_service.send_email(
                to_email=email,
                subject=request.subject,
                message=personalized_message
            )

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

