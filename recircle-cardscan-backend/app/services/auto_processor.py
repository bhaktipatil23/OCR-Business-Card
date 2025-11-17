import asyncio
import time
from app.services.queue_manager import queue_manager
from app.services.websocket_manager import websocket_manager

class AutoProcessor:
    """Automatically processes all files in queue sequentially"""
    
    def __init__(self):
        self._processing_tasks = {}
    
    async def start_batch_processing(self, batch_id: str):
        """Start automatic processing of entire batch"""
        if batch_id in self._processing_tasks:
            return  # Already processing
        
        # Create processing task
        task = asyncio.create_task(self._process_batch_sequentially(batch_id))
        self._processing_tasks[batch_id] = task
        
        try:
            await task
        finally:
            # Clean up task
            if batch_id in self._processing_tasks:
                del self._processing_tasks[batch_id]
    
    async def _process_batch_sequentially(self, batch_id: str):
        """Process all files in batch one by one"""
        
        while True:
            # Get next file from input queue
            file_info = queue_manager.get_next_from_input_queue(batch_id)
            
            if not file_info:
                # No more files to process
                await self._send_batch_complete(batch_id)
                break
            
            # Process single file
            await self._process_single_file(batch_id, file_info)
            
            # Small delay between files
            await asyncio.sleep(0.5)
    
    async def _process_single_file(self, batch_id: str, file_info: dict):
        """Process single file with WebSocket updates"""
        
        file_id = file_info["file_id"]
        filename = file_info["filename"]
        file_path = file_info["file_path"]
        
        try:
            start_time = time.time()
            
            # Stage 1: Start processing
            await websocket_manager.broadcast(batch_id, {
                "type": "file_update",
                "file_id": file_id,
                "filename": filename,
                "status": "processing",
                "stage": "started",
                "progress": 0
            })
            
            # Stage 2: Validation
            queue_manager.update_input_status(batch_id, file_id, "validating")
            await websocket_manager.broadcast(batch_id, {
                "type": "file_update",
                "file_id": file_id,
                "filename": filename,
                "status": "validating",
                "stage": "validation",
                "progress": 25
            })
            
            # Call validation
            from app.services.business_card_validator import BusinessCardValidator
            validator = BusinessCardValidator()
            validation_result = await validator.validate_business_card(file_path)
            
            # Send validation result
            await websocket_manager.broadcast(batch_id, {
                "type": "validation_result",
                "file_id": file_id,
                "filename": filename,
                "is_valid": validation_result["is_business_card"],
                "confidence": validation_result.get("confidence", "Unknown"),
                "reasoning": validation_result.get("reasoning", "")
            })
            
            if not validation_result["is_business_card"]:
                # Invalid - mark as failed and continue to next
                queue_manager.update_input_status(batch_id, file_id, "invalid")
                await websocket_manager.broadcast(batch_id, {
                    "type": "file_update",
                    "file_id": file_id,
                    "filename": filename,
                    "status": "invalid",
                    "stage": "validation_failed",
                    "progress": 100
                })
                return
            
            # Stage 3: Extraction
            queue_manager.update_input_status(batch_id, file_id, "extracting")
            await websocket_manager.broadcast(batch_id, {
                "type": "file_update",
                "file_id": file_id,
                "filename": filename,
                "status": "extracting",
                "stage": "extraction",
                "progress": 50
            })
            
            # Call Gemini extraction
            from app.services.gemini_service import GeminiService
            gemini_service = GeminiService()
            extracted_records = await gemini_service.extract_document_data(file_path)
            
            if not extracted_records or len(extracted_records) == 0:
                # Extraction failed
                queue_manager.update_input_status(batch_id, file_id, "extraction_failed")
                await websocket_manager.broadcast(batch_id, {
                    "type": "file_update",
                    "file_id": file_id,
                    "filename": filename,
                    "status": "extraction_failed",
                    "stage": "extraction_failed",
                    "progress": 100
                })
                return
            
            # Stage 4: Processing data
            queue_manager.update_input_status(batch_id, file_id, "processing_data")
            await websocket_manager.broadcast(batch_id, {
                "type": "file_update",
                "file_id": file_id,
                "filename": filename,
                "status": "processing_data",
                "stage": "processing_data",
                "progress": 75
            })
            
            # Clean extracted data
            processed_data = extracted_records[0]
            
            # Clean phone numbers
            if "phone" in processed_data and processed_data["phone"]:
                phone = processed_data["phone"]
                if len(phone.replace(",", "").replace(" ", "")) > 10 and phone.startswith("91"):
                    phone = phone[2:]
                processed_data["phone"] = phone
            
            # Stage 5: Completion
            processing_time = time.time() - start_time
            
            # Add to output queue
            queue_manager.add_to_output_queue(batch_id, file_id, processed_data, processing_time)
            
            # Send completion
            await websocket_manager.broadcast(batch_id, {
                "type": "extraction_complete",
                "file_id": file_id,
                "filename": filename,
                "status": "completed",
                "stage": "completed",
                "progress": 100,
                "extracted_data": processed_data,
                "processing_time": processing_time
            })
            
            # Send batch summary
            summary = queue_manager.get_batch_summary(batch_id)
            await websocket_manager.broadcast(batch_id, {
                "type": "batch_update",
                "batch_id": batch_id,
                "summary": summary
            })
            
        except Exception as e:
            # Handle errors
            queue_manager.update_input_status(batch_id, file_id, "failed")
            await websocket_manager.broadcast(batch_id, {
                "type": "error",
                "file_id": file_id,
                "filename": filename,
                "error": str(e),
                "status": "failed"
            })
    
    async def _send_batch_complete(self, batch_id: str):
        """Send batch completion message"""
        summary = queue_manager.get_batch_summary(batch_id)
        
        await websocket_manager.broadcast(batch_id, {
            "type": "batch_complete",
            "batch_id": batch_id,
            "summary": summary,
            "download_url": f"/api/v1/download/{batch_id}",
            "message": "All files processed successfully!"
        })

# Global instance
auto_processor = AutoProcessor()