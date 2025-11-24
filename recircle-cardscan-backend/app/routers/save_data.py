from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List
import mysql.connector
from app.config import settings

router = APIRouter(prefix="/api/v1", tags=["save-data"])

# Store last request data for download fallback
last_request_data = {}

class SaveDataRequest(BaseModel):
    name: str
    team: str
    event: str
    batch_id: str
    extracted_data: List[dict]

@router.post("/save-data")
async def save_data(request: SaveDataRequest):
    """Save form data and extracted data to database"""
    conn = None
    cursor = None
    
    try:
        print(f"[SAVE] Attempting to save data for batch {request.batch_id}")
        
        # Store request data for download fallback
        global last_request_data
        last_request_data = {
            'batch_id': request.batch_id,
            'extracted_data': request.extracted_data
        }
        
        conn = mysql.connector.connect(
            host=settings.DB_HOST,
            port=settings.DB_PORT,
            user=settings.DB_USER,
            password=settings.DB_PASSWORD,
            database=settings.DB_NAME
        )
        cursor = conn.cursor()
        
        # Check if batch already exists
        check_query = "SELECT COUNT(*) FROM events WHERE batch_id = %s"
        cursor.execute(check_query, (request.batch_id,))
        exists = cursor.fetchone()[0] > 0
        
        if exists:
            print(f"[SAVE] Batch {request.batch_id} already exists, skipping event insert")
        else:
            # Insert event data
            event_query = """
            INSERT INTO events (name, team, batch_id, event)
            VALUES (%s, %s, %s, %s)
            """
            cursor.execute(event_query, (
                request.name,
                request.team,
                request.batch_id,
                request.event
            ))
            print(f"[SAVE] Inserted event data for batch {request.batch_id}")
        
        # Insert extracted business card data with duplicate prevention
        card_query = """
        INSERT INTO business_cards (batch_id, name, phone, email, company, designation, address)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        
        check_duplicate_query = """
        SELECT COUNT(*) FROM business_cards WHERE batch_id = %s AND phone = %s
        """
        
        saved_count = 0
        skipped_count = 0
        for item in request.extracted_data:
            phone = item.get('phone', '')
            
            # Check if this phone number already exists for this batch
            cursor.execute(check_duplicate_query, (request.batch_id, phone))
            exists = cursor.fetchone()[0] > 0
            
            if exists:
                print(f"[SAVE] Duplicate phone {phone} found, skipping")
                skipped_count += 1
                continue
                
            try:
                cursor.execute(card_query, (
                    request.batch_id,
                    item.get('name', ''),
                    phone,
                    item.get('email', ''),
                    item.get('company', ''),
                    item.get('designation', ''),
                    item.get('address', '')
                ))
                saved_count += 1
            except mysql.connector.IntegrityError as ie:
                print(f"[SAVE] Database integrity error, skipping: {ie}")
                skipped_count += 1
                continue
        
        conn.commit()
        print(f"[SAVE] Successfully saved {saved_count} business cards")
        
        return {
            "status": "success",
            "message": f"Successfully saved event and {saved_count} business cards" + (f" ({skipped_count} duplicates skipped)" if skipped_count > 0 else ""),
            "saved_count": saved_count,
            "skipped_count": skipped_count
        }
        
    except mysql.connector.Error as db_error:
        print(f"[SAVE] Database error: {str(db_error)}")
        if conn:
            conn.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(db_error)}")
    except Exception as e:
        print(f"[SAVE] General error: {str(e)}")
        if conn:
            conn.rollback()
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

@router.post("/save-email-data")
async def save_email_data(request: SaveDataRequest):
    """Save email campaign data to database"""
    print(f"[EMAIL-SAVE] Processing email save request for batch {request.batch_id}")
    return await save_data(request)