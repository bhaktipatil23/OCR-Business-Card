"""
Email Service for sending emails via SMTP
"""
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app.config import settings
import logging

logger = logging.getLogger(__name__)


class EmailService:
    """Service for sending emails using SMTP"""

    @staticmethod
    async def send_email(
        to_email: str,
        subject: str,
        message: str,
        html_message: str = None
    ) -> bool:
        """
        Send an email via SMTP

        Args:
            to_email: Recipient email address
            subject: Email subject
            message: Plain text message
            html_message: Optional HTML version of the message

        Returns:
            bool: True if email sent successfully, False otherwise
        """
        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['From'] = f"{settings.EMAIL_FROM_NAME} <{settings.EMAIL_FROM}>"
            msg['To'] = to_email
            msg['Subject'] = subject

            # Add plain text part
            text_part = MIMEText(message, 'plain')
            msg.attach(text_part)

            # Add HTML part if provided
            if html_message:
                html_part = MIMEText(html_message, 'html')
                msg.attach(html_part)

            # Connect to SMTP server
            logger.debug(f"Connecting to SMTP: {settings.SMTP_HOST}:{settings.SMTP_PORT}")
            with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT, timeout=30) as server:
                logger.debug("Starting TLS encryption...")
                server.starttls()  # Enable TLS encryption

                logger.debug(f"Authenticating as {settings.SMTP_USER}...")
                server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
                logger.debug("Authentication successful")

                logger.debug(f"Sending message to {to_email}...")
                server.send_message(msg)

            logger.info(f"✓ Email sent successfully to {to_email}")
            return True

        except smtplib.SMTPAuthenticationError as e:
            logger.error(f"✗ SMTP Authentication failed for {to_email}: {str(e)}")
            logger.error("Please check SMTP username and password in .env file")
            return False

        except smtplib.SMTPException as e:
            logger.error(f"✗ SMTP error sending to {to_email}: {str(e)}")
            return False

        except Exception as e:
            logger.error(f"✗ Failed to send email to {to_email}: {str(e)}")
            return False

    @staticmethod
    async def send_bulk_emails(
        recipients: list,
        subject: str,
        get_message_func
    ) -> dict:
        """
        Send emails to multiple recipients

        Args:
            recipients: List of recipient email addresses
            subject: Email subject
            get_message_func: Function that takes email and returns (message, html_message) tuple

        Returns:
            dict: Statistics about sent emails
        """
        results = {
            'total': len(recipients),
            'sent': 0,
            'failed': 0,
            'details': []
        }

        for email in recipients:
            try:
                message, html_message = get_message_func(email)
                success = await EmailService.send_email(
                    to_email=email,
                    subject=subject,
                    message=message,
                    html_message=html_message
                )

                if success:
                    results['sent'] += 1
                    results['details'].append({
                        'email': email,
                        'status': 'sent',
                        'error': None
                    })
                else:
                    results['failed'] += 1
                    results['details'].append({
                        'email': email,
                        'status': 'failed',
                        'error': 'Failed to send'
                    })

            except Exception as e:
                results['failed'] += 1
                results['details'].append({
                    'email': email,
                    'status': 'failed',
                    'error': str(e)
                })
                logger.error(f"Error sending email to {email}: {str(e)}")

        return results


# Create singleton instance
email_service = EmailService()
