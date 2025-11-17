from app.services.gemini_service import GeminiService
from app.services.csv_writer import CSVWriter
from app.services.pdf_converter import PDFConverter
from app.core.resource_manager import resource_manager
from app.core.data_store import data_store
from app.utils.logger import app_logger

from typing import List, Dict
import os
import asyncio


class FileProcessor:
    
    def __init__(self, batch_id: str):
        self.batch_id = batch_id
        self.gemini_service = GeminiService()
        self.pdf_converter = PDFConverter()
        import threading

        self.processed_count = 0
        self.processed_files = set()
        self._lock = threading.Lock()
        
        self.all_extracted_records = []
        self.records_lock = threading.Lock()
        
        # Import processing status from process.py
        from app.routers.process import processing_status, status_lock
        self.processing_status = processing_status
        self.status_lock = status_lock
    

    
    async def process_single_file(self, file_info: Dict) -> None:
        """Process one file through complete cycle with card side merging"""
        await resource_manager.acquire_file_slot(self.batch_id)
        
        try:
            file_key = f"{file_info['filename']}_{file_info.get('file_id', '')}"
            if file_key in self.processed_files:
                return
            
            # Update current file being processed
            self._update_processing_status(file_info['filename'])
            
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
                        app_logger.info(f"[QUEUE] Added record to queue: {record['name']} from {record['filename']}")
                    else:
                        app_logger.info(f"[QUEUE] Skipped record with too many N/A fields: {record['filename']}")
            
            with self._lock:
                self.processed_count += 1
                current_count = self.processed_count
            
            # Update progress after each file
            self._update_progress(current_count)
            
        except Exception as e:
            app_logger.error(f"[PROCESSOR] Error with {file_info['filename']}: {str(e)}")
            import traceback
            traceback.print_exc()
            raise e
        finally:
            resource_manager.release_file_slot(self.batch_id)
    
    async def process_all_files(self, files_list: List[Dict]) -> Dict:
        """Process all uploaded files with fair resource allocation"""
        app_logger.info(f"[PROCESSOR] Starting queue-based processing for {len(files_list)} files in batch {self.batch_id}")
        
        semaphore = asyncio.Semaphore(3)
        
        async def process_with_semaphore(file_info):
            async with semaphore:
                await self.process_single_file(file_info)
        
        tasks = [process_with_semaphore(file_info) for file_info in files_list]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Log any exceptions
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                app_logger.error(f"[QUEUE] Error processing file {files_list[i]['filename']}: {result}")
        
        # Store extracted records in memory (CSV will be generated on download)
        final_records = self.all_extracted_records
        data_store.store_batch_data(self.batch_id, final_records)
        
        app_logger.info(f"[QUEUE] All files processed. Queue contains {len(final_records)} records")
        app_logger.info(f"[PROCESSOR] Completed {self.batch_id}: {self.processed_count}/{len(files_list)} files, {len(final_records)} records")
        
        return {
            "status": "completed",
            "total_processed": self.processed_count,
            "records_count": len(final_records),
            "extracted_data": final_records,
            "queue_summary": f"Processed {len(files_list)} files, queued {len(final_records)} valid records"
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
        """Create single CSV record per business card"""
        return [{
            "file_id": record.get('file_id', 'unknown'),
            "filename": record.get('filename', 'N/A'),
            "name": record.get('name', 'N/A'),
            "phone": record.get('phone', 'N/A'),
            "email": record.get('email', 'N/A'),
            "company": record.get('company', 'N/A'),
            "designation": record.get('designation', 'N/A'),
            "address": record.get('address', 'N/A')
        }]
    
    def _update_processing_status(self, current_filename: str):
        """Update the current file being processed"""
        with self.status_lock:
            if self.batch_id in self.processing_status:
                self.processing_status[self.batch_id]["current_file"] = current_filename
    
    def _update_progress(self, processed_count: int):
        """Update the progress count"""
        with self.status_lock:
            if self.batch_id in self.processing_status:
                self.processing_status[self.batch_id]["processed"] = processed_count
    
