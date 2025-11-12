import csv
import os
from app.config import settings
from typing import Dict, Set

class CSVWriter:
    
    def __init__(self, batch_id: str):
        self.batch_id = batch_id
        self.csv_path = os.path.join(settings.OUTPUT_CSV_PATH, f"{batch_id}_data.csv")
        self.headers = ["name", "phone", "email", "company", "designation", "address", "remarks"]
        self.written_records: Set[str] = set()
        self._initialize_csv()
    
    def _initialize_csv(self):
        """Create CSV with headers"""
        os.makedirs(settings.OUTPUT_CSV_PATH, exist_ok=True)
        
        with open(self.csv_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(self.headers)
        print(f"📝 Created CSV: {self.csv_path}")
    
    def write_record(self, record: Dict) -> None:
        """Append single record to CSV with deduplication"""
        # Create unique key for deduplication
        record_key = f"{record.get('name', '')}|{record.get('phone', '')}|{record.get('email', '')}|{record.get('company', '')}|{record.get('designation', '')}"
        
        # Skip if already written
        if record_key in self.written_records:
            print(f"⚠️ Skipping duplicate: {record['file_id']}")
            return
        
        # Add to written records
        self.written_records.add(record_key)
        
        with open(self.csv_path, 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([
                record.get("name", ""),
                record.get("phone", ""),
                record.get("email", ""),
                record.get("company", ""),
                record.get("designation", ""),
                record.get("address", ""),
                ""
            ])
        print(f"✅ Written to CSV: {record['file_id']}")
    
    def get_csv_path(self) -> str:
        return self.csv_path
    
    def clear_duplicates(self) -> None:
        """Clear the deduplication set for new batch"""
        self.written_records.clear()