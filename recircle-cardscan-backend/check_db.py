import mysql.connector
import os
from dotenv import load_dotenv

load_dotenv()

try:
    conn = mysql.connector.connect(
        host=os.getenv('DB_HOST', 'localhost'),
        port=int(os.getenv('DB_PORT', 3306)),
        user=os.getenv('DB_USER', 'root'),
        password=os.getenv('DB_PASSWORD', 'NewPassword123!'),
        database=os.getenv('DB_NAME', 'business_card_ocr')
    )
    cursor = conn.cursor(dictionary=True)
    
    # Check what batch_ids exist
    cursor.execute("SELECT DISTINCT batch_id FROM business_cards LIMIT 10")
    batches = cursor.fetchall()
    print("Available batch_ids:")
    for batch in batches:
        print(f"  - {batch['batch_id']}")
    
    # Check data for a specific batch
    if batches:
        batch_id = batches[0]['batch_id']
        cursor.execute("SELECT * FROM business_cards WHERE batch_id = %s LIMIT 5", (batch_id,))
        cards = cursor.fetchall()
        print(f"\nSample data for {batch_id}:")
        for card in cards:
            print(f"  Name: {card.get('name', 'N/A')}")
            print(f"  Phone: {card.get('phone', 'N/A')}")
            print(f"  Email: {card.get('email', 'N/A')}")
            print(f"  Company: {card.get('company', 'N/A')}")
            print("  ---")
    
    cursor.close()
    conn.close()
    
except Exception as e:
    print(f"Error: {e}")