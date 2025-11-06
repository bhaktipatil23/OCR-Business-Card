from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any
import pandas as pd
import os
from app.config import settings

router = APIRouter(prefix="/api/v1", tags=["extracted-data"])

@router.get("/extracted-data/{batch_id}")
async def get_extracted_data(batch_id: str):
    """Get extracted data for a batch"""
    try:
        # Try different possible CSV file names
        possible_names = [
            f"{batch_id}_data.csv",
            f"batch_{batch_id}_data.csv"
        ]
        
        csv_path = None
        for name in possible_names:
            potential_path = os.path.join(settings.OUTPUT_CSV_PATH, name)
            if os.path.exists(potential_path):
                csv_path = potential_path
                break
        
        if not csv_path:
            # List all CSV files in the directory for debugging
            csv_files = [f for f in os.listdir(settings.OUTPUT_CSV_PATH) if f.endswith('.csv')]
            print(f"Available CSV files: {csv_files}")
            print(f"Looking for batch_id: {batch_id}")
            raise HTTPException(status_code=404, detail=f"Extracted data not found. Available files: {csv_files}")
        

        
        # Read CSV file and handle NaN values
        df = pd.read_csv(csv_path)
        df = df.fillna('N/A')  # Replace NaN with 'N/A'
        print(f"CSV columns: {df.columns.tolist()}")
        print(f"CSV shape: {df.shape}")
        print(f"First few rows: {df.head()}")
        
        # Group by file_id and convert to required format
        result = []
        for file_id in df['file_id'].unique():
            file_data = df[df['file_id'] == file_id]
            filename = file_data['filename'].iloc[0] if 'filename' in df.columns and not file_data['filename'].empty else "unknown"
            
            extracted_data = []
            for _, row in file_data.iterrows():
                # Handle NaN values properly
                name = row.get('name', 'N/A')
                phone = row.get('phone', 'N/A')
                email = row.get('email', 'N/A')
                company = row.get('company', 'N/A')
                designation = row.get('designation', 'N/A')
                address = row.get('address', 'N/A')
                
                # Convert to string and handle NaN
                extracted_data.append({
                    "name": str(name) if pd.notna(name) else 'N/A',
                    "phone": str(phone) if pd.notna(phone) else 'N/A',
                    "email": str(email) if pd.notna(email) else 'N/A',
                    "company": str(company) if pd.notna(company) else 'N/A',
                    "designation": str(designation) if pd.notna(designation) else 'N/A',
                    "address": str(address) if pd.notna(address) else 'N/A'
                })
            
            result.append({
                "file_id": file_id,
                "filename": filename,
                "extracted_data": extracted_data
            })
        
        print(f"Returning {len(result)} files with extracted data")
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading extracted data: {str(e)}")