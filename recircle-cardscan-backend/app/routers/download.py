from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from app.services.csv_writer import CSVWriter
import os

router = APIRouter(prefix="/api/v1", tags=["download"])

@router.get("/download/{batch_id}")
async def download_csv(batch_id: str):
    """Download CSV from recent session data"""
    try:
        import csv
        import tempfile
        from app.services.queue_manager import queue_manager
        
        # Get completed data from output queue
        cards_data = queue_manager.get_all_outputs(batch_id)
        
        # Fallback to save-data request storage
        if not cards_data:
            try:
                from app.routers.save_data import last_request_data
                if last_request_data.get('batch_id') == batch_id:
                    cards_data = last_request_data.get('extracted_data', [])
            except:
                pass
        
        if not cards_data:
            raise HTTPException(status_code=404, detail="No recent data found for this session")
        
        # Get custom filename
        custom_filename = f"{batch_id}_data.csv"
        
        # Create temporary CSV file
        temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv', encoding='utf-8')
        writer = csv.writer(temp_file, quoting=csv.QUOTE_ALL)
        
        # Write headers
        writer.writerow(["name", "phone", "email", "company", "designation", "address", "remarks"])
        
        # Write data with tab prefix for phone numbers
        for card in cards_data:
            phone = card.get('phone', '')
            if phone and phone != "N/A":
                phone = "\t" + phone
            
            writer.writerow([
                card.get('name', ''),
                phone,
                card.get('email', ''),
                card.get('company', ''),
                card.get('designation', ''),
                card.get('address', ''),
                ""
            ])
        
        temp_file.close()
        
        return FileResponse(
            path=temp_file.name,
            media_type="application/octet-stream",
            filename=custom_filename,
            headers={"Content-Disposition": f"attachment; filename={custom_filename}"}
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@router.get("/download-latest")
async def download_latest_data():
    """Download CSV from most recent batch data"""
    try:
        import mysql.connector
        import os as env_os
        import csv
        import tempfile
        
        conn = mysql.connector.connect(
            host=env_os.getenv('DB_HOST', 'localhost'),
            port=int(env_os.getenv('DB_PORT', 3306)),
            user=env_os.getenv('DB_USER', 'root'),
            password=env_os.getenv('DB_PASSWORD', 'NewPassword123!'),
            database=env_os.getenv('DB_NAME', 'business_card_ocr')
        )
        cursor = conn.cursor(dictionary=True)
        
        # Get most recent batch_id
        cursor.execute("SELECT batch_id FROM business_cards ORDER BY id DESC LIMIT 1")
        latest_batch = cursor.fetchone()
        
        if not latest_batch:
            raise HTTPException(status_code=404, detail="No data found")
        
        batch_id = latest_batch['batch_id']
        
        # Get unique business cards data
        query = """
        SELECT name, phone, email, company, designation, address 
        FROM business_cards 
        WHERE batch_id = %s 
        GROUP BY phone
        ORDER BY id DESC
        """
        cursor.execute(query, (batch_id,))
        cards_data = cursor.fetchall()
        
        # Get custom filename
        query2 = "SELECT name, event FROM events WHERE batch_id = %s LIMIT 1"
        cursor.execute(query2, (batch_id,))
        form_data = cursor.fetchone()
        
        custom_filename = f"{batch_id}_data.csv"
        if form_data:
            name = form_data['name'].replace(' ', '_')
            event = form_data['event'].replace(' ', '_')
            custom_filename = f"{name}_{event}.csv"
        
        cursor.close()
        conn.close()
        
        # Create temporary CSV file
        temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv', encoding='utf-8')
        writer = csv.writer(temp_file, quoting=csv.QUOTE_ALL)
        
        # Write headers
        writer.writerow(["name", "phone", "email", "company", "designation", "address", "remarks"])
        
        # Write data with tab prefix for phone numbers
        for card in cards_data:
            phone = card['phone']
            if phone and phone != "N/A":
                phone = "\t" + phone
            
            writer.writerow([
                card['name'] or "",
                phone,
                card['email'] or "",
                card['company'] or "",
                card['designation'] or "",
                card['address'] or "",
                ""
            ])
        
        temp_file.close()
        
        return FileResponse(
            path=temp_file.name,
            media_type="application/octet-stream",
            filename=custom_filename,
            headers={"Content-Disposition": f"attachment; filename={custom_filename}"}
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@router.get("/download-saved/{batch_id}")
async def download_saved_data(batch_id: str):
    """Download CSV from saved database data"""
    try:
        import mysql.connector
        import os as env_os
        import csv
        import tempfile
        
        conn = mysql.connector.connect(
            host=env_os.getenv('DB_HOST', 'localhost'),
            port=int(env_os.getenv('DB_PORT', 3306)),
            user=env_os.getenv('DB_USER', 'root'),
            password=env_os.getenv('DB_PASSWORD', 'NewPassword123!'),
            database=env_os.getenv('DB_NAME', 'business_card_ocr')
        )
        cursor = conn.cursor(dictionary=True)
        
        # Get unique business cards data (remove duplicates by phone)
        query = """
        SELECT name, phone, email, company, designation, address 
        FROM business_cards 
        WHERE batch_id = %s 
        GROUP BY phone
        ORDER BY id DESC
        """
        cursor.execute(query, (batch_id,))
        cards_data = cursor.fetchall()
        
        if not cards_data:
            raise HTTPException(status_code=404, detail="No data found for this batch")
        
        # Get custom filename
        query2 = "SELECT name, event FROM events WHERE batch_id = %s LIMIT 1"
        cursor.execute(query2, (batch_id,))
        form_data = cursor.fetchone()
        
        custom_filename = f"{batch_id}_data.csv"
        if form_data:
            name = form_data['name'].replace(' ', '_')
            event = form_data['event'].replace(' ', '_')
            custom_filename = f"{name}_{event}.csv"
        
        cursor.close()
        conn.close()
        
        # Create temporary CSV file
        temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv', encoding='utf-8')
        writer = csv.writer(temp_file, quoting=csv.QUOTE_ALL)
        
        # Write headers
        writer.writerow(["name", "phone", "email", "company", "designation", "address", "remarks"])
        
        # Write data with tab prefix for phone numbers
        for card in cards_data:
            phone = card['phone']
            if phone and phone != "N/A":
                phone = "\t" + phone
            
            writer.writerow([
                card['name'],
                phone,
                card['email'],
                card['company'],
                card['designation'],
                card['address'],
                ""
            ])
        
        temp_file.close()
        
        return FileResponse(
            path=temp_file.name,
            media_type="application/octet-stream",
            filename=custom_filename,
            headers={"Content-Disposition": f"attachment; filename={custom_filename}"}
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")