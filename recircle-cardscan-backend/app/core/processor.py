from app.services.gemini_service import GeminiService
from app.services.csv_writer import CSVWriter
from app.services.pdf_converter import PDFConverter
from app.core.resource_manager import resource_manager
from app.utils.logger import app_logger

from typing import List, Dict
import os
import asyncio


class FileProcessor:
    
    def __init__(self, batch_id: str):
        self.batch_id = batch_id
        self.gemini_service = GeminiService()
        self.csv_writer = CSVWriter(batch_id)
        import threading
        self._csv_lock = threading.Lock()
        self.pdf_converter = PDFConverter()

        self.processed_count = 0
        self.processed_files = set()
        self._lock = threading.Lock()
        
        self.all_extracted_records = []
        self.records_lock = threading.Lock()
    

    
    async def process_single_file(self, file_info: Dict) -> None:
        """Process one file through complete cycle with card side merging"""
        await resource_manager.acquire_file_slot(self.batch_id)
        
        try:
            file_key = f"{file_info['filename']}_{file_info.get('file_id', '')}"
            if file_key in self.processed_files:
                pass
                return
            
            pass
            
            self.processed_files.add(file_key)
            
            # Handle PDF or Image
            if file_info['file_type'] == 'application/pdf':
                images = self.pdf_converter.convert_pdf_to_images(file_info['file_path'])
                if not images:
                    return
                
                all_extracted_data = []
                temp_image_paths = []
                
                for page_num, image in enumerate(images):
                    temp_image_path = file_info['file_path'].replace('.pdf', f'_page{page_num+1}.jpg')
                    image.save(temp_image_path)
                    temp_image_paths.append(temp_image_path)
                    
                    page_data = await self.gemini_service.extract_document_data(temp_image_path)
                    all_extracted_data.extend(page_data)
                
                for temp_path in temp_image_paths:
                    os.remove(temp_path)
                
                extracted_records = self._combine_multi_page_data(all_extracted_data)
            else:
                processing_path = file_info['file_path']
                
                extracted_records = await self.gemini_service.extract_document_data(processing_path)
            
            pass
            
            # Store extracted records
            with self.records_lock:
                for extracted_data in extracted_records:
                    record = {
                        "file_id": file_info["file_id"],
                        "filename": file_info["filename"],
                
                        "name": extracted_data.get("name", "N/A"),
                        "phone": extracted_data.get("phone", "N/A"),
                        "email": extracted_data.get("email", "N/A"),
                        "company": extracted_data.get("company", "N/A"),
                        "designation": extracted_data.get("designation", "N/A"),
                        "address": extracted_data.get("address", "N/A"),
                
                    }
                    
                    # Check if record has enough valid data (max 2 N/A fields allowed)
                    na_count = sum(1 for field in ['name', 'phone', 'email', 'company', 'designation', 'address'] 
                                  if record[field] == 'N/A')
                    
                    if na_count <= 2:
                        self.all_extracted_records.append(record)
                        pass
                    else:
                        pass
            
            with self._lock:
                self.processed_count += 1
                current_count = self.processed_count
            pass
            
        except Exception as e:
            app_logger.error(f"[PROCESSOR] Error with {file_info['filename']}: {str(e)}")
            import traceback
            traceback.print_exc()
            raise e
        finally:
            resource_manager.release_file_slot(self.batch_id)
    
    async def process_all_files(self, files_list: List[Dict]) -> Dict:
        """Process all uploaded files with fair resource allocation"""
        app_logger.info(f"[PROCESSOR] Processing {len(files_list)} files for {self.batch_id}")
        
        semaphore = asyncio.Semaphore(3)
        
        async def process_with_semaphore(file_info):
            async with semaphore:
                await self.process_single_file(file_info)
        
        tasks = [process_with_semaphore(file_info) for file_info in files_list]
        await asyncio.gather(*tasks, return_exceptions=True)
        
        # Write all extracted records to CSV
        final_records = self.all_extracted_records
        for record in final_records:
            # Double-check record validity before writing to CSV
            na_count = sum(1 for field in ['name', 'phone', 'email', 'company', 'designation', 'address'] 
                          if record.get(field, 'N/A') == 'N/A')
            
            if na_count <= 2:
                csv_records = self._create_csv_records(record)
                for csv_record in csv_records:
                    with self._csv_lock:
                        self.csv_writer.write_record(csv_record)
            else:
                pass
        
        app_logger.info(f"[PROCESSOR] Completed {self.batch_id}: {self.processed_count}/{len(files_list)} files, {len(final_records)} records")
        
        return {
            "status": "completed",
            "total_processed": self.processed_count,
            "csv_path": self.csv_writer.get_csv_path()
        }
    
    def _combine_multi_page_data(self, all_data: List[Dict]) -> List[Dict]:
        """Combine data from multiple pages into complete records"""
        if not all_data:
            return []
        
        if len(all_data) == 1:
            return all_data
        
        pass
        
        merged_record = {
            "name": "N/A",
            "phone": "N/A", 
            "email": "N/A",
            "company": "N/A",
            "designation": "N/A",
            "address": "N/A"
        }
        
        all_phones = []
        all_emails = []
        all_companies = []
        
        for record in all_data:
            if merged_record["name"] == "N/A" and record.get("name", "N/A") != "N/A":
                merged_record["name"] = record["name"]
            
            if record.get("phone", "N/A") != "N/A":
                phones = [p.strip() for p in record["phone"].split(',') if p.strip()]
                all_phones.extend(phones)
            
            if record.get("email", "N/A") != "N/A":
                emails = [e.strip() for e in record["email"].split(',') if e.strip()]
                all_emails.extend(emails)
            
            if record.get("company", "N/A") != "N/A":
                all_companies.append(record["company"])
            
            if merged_record["designation"] == "N/A" and record.get("designation", "N/A") != "N/A":
                merged_record["designation"] = record["designation"]
            
            if merged_record["address"] == "N/A" and record.get("address", "N/A") != "N/A":
                merged_record["address"] = record["address"]
        
        if all_phones:
            merged_record["phone"] = ','.join(list(dict.fromkeys(all_phones)))
        
        if all_emails:
            merged_record["email"] = ','.join(list(dict.fromkeys(all_emails)))
        
        if all_companies:
            merged_record["company"] = max(all_companies, key=len)
        
        return [merged_record]
    
    def _create_csv_records(self, record: Dict) -> List[Dict]:
        """Create CSV records with phone number splitting for final output"""
        records = []
        
        phone_str = record.get('phone', 'N/A')
        phones = []
        
        if phone_str and phone_str != 'N/A':
            for phone in phone_str.split(','):
                clean_phone = phone.strip()
                if clean_phone and clean_phone not in phones:
                    phones.append(clean_phone)
        
        email_str = record.get('email', 'N/A')
        emails = []
        if email_str and email_str != 'N/A':
            emails = [e.strip() for e in email_str.split(',') if e.strip()]
        
        first_record = {
            "file_id": record.get('file_id', 'unknown'),
            "name": record.get('name', 'N/A'),
            "phone": phones[0] if phones else 'N/A',
            "email": emails[0] if emails else 'N/A',
            "company": record.get('company', 'N/A'),
            "designation": record.get('designation', 'N/A'),
            "address": record.get('address', 'N/A')
        }
        records.append(first_record)
        
        for i, phone in enumerate(phones[1:], 1):
            additional_record = {
                "file_id": record.get('file_id', 'unknown'),
                "name": "",
                "phone": phone,
                "email": emails[i] if i < len(emails) else "",
                "company": "",
                "designation": "",
                "address": ""
            }
            records.append(additional_record)
        
        return records
    
