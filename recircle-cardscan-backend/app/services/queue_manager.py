import threading
import time
from typing import Dict, List, Optional
from datetime import datetime

class QueueManager:
    """Dual queue system for sequential processing"""
    
    def __init__(self):
        self._batches: Dict[str, Dict] = {}
        self._lock = threading.Lock()
    
    def initialize_batch(self, batch_id: str, files_list: List[Dict]) -> None:
        """Initialize batch with input queue"""
        with self._lock:
            self._batches[batch_id] = {
                "input_queue": [
                    {
                        "file_id": file_info["file_id"],
                        "filename": file_info["filename"],
                        "file_path": file_info["file_path"],
                        "status": "waiting",
                        "position": i + 1,
                        "uploaded_at": datetime.now().isoformat()
                    }
                    for i, file_info in enumerate(files_list)
                ],
                "output_queue": [],
                "metadata": {
                    "total": len(files_list),
                    "completed": 0,
                    "processing": 0,
                    "waiting": len(files_list),
                    "failed": 0,
                    "current_file_id": None
                }
            }
    
    def get_next_from_input_queue(self, batch_id: str) -> Optional[Dict]:
        """Get next file from input queue"""
        with self._lock:
            if batch_id not in self._batches:
                return None
            
            input_queue = self._batches[batch_id]["input_queue"]
            for file_info in input_queue:
                if file_info["status"] == "waiting":
                    file_info["status"] = "processing"
                    self._batches[batch_id]["metadata"]["current_file_id"] = file_info["file_id"]
                    self._update_metadata(batch_id)
                    return file_info.copy()
            return None
    
    def update_input_status(self, batch_id: str, file_id: str, status: str) -> None:
        """Update file status in input queue"""
        with self._lock:
            if batch_id not in self._batches:
                return
            
            input_queue = self._batches[batch_id]["input_queue"]
            for file_info in input_queue:
                if file_info["file_id"] == file_id:
                    file_info["status"] = status
                    break
            
            self._update_metadata(batch_id)
    
    def add_to_output_queue(self, batch_id: str, file_id: str, extracted_data: Dict, processing_time: float) -> None:
        """Add completed file to output queue with same file_id"""
        with self._lock:
            if batch_id not in self._batches:
                return
            
            # Find file in input queue
            input_file = None
            for file_info in self._batches[batch_id]["input_queue"]:
                if file_info["file_id"] == file_id:
                    input_file = file_info
                    break
            
            if input_file:
                # Add to output queue with same file_id
                output_item = {
                    "file_id": file_id,  # SAME ID
                    "filename": input_file["filename"],
                    "status": "completed",
                    "extracted_data": extracted_data,
                    "processing_time": processing_time,
                    "completed_at": datetime.now().isoformat()
                }
                
                self._batches[batch_id]["output_queue"].append(output_item)
                
                # Update input queue status
                input_file["status"] = "completed"
                
                self._update_metadata(batch_id)
    
    def get_file_pair(self, batch_id: str, file_id: str) -> Dict:
        """Get both input and output for same file_id"""
        with self._lock:
            if batch_id not in self._batches:
                return {"input": None, "output": None}
            
            batch = self._batches[batch_id]
            
            # Find in input queue
            input_file = None
            for file_info in batch["input_queue"]:
                if file_info["file_id"] == file_id:
                    input_file = file_info.copy()
                    break
            
            # Find in output queue
            output_file = None
            for file_info in batch["output_queue"]:
                if file_info["file_id"] == file_id:
                    output_file = file_info.copy()
                    break
            
            return {"input": input_file, "output": output_file}
    
    def get_all_outputs(self, batch_id: str) -> List[Dict]:
        """Get all completed outputs for CSV"""
        with self._lock:
            if batch_id not in self._batches:
                return []
            
            outputs = []
            for output in self._batches[batch_id]["output_queue"]:
                outputs.append({
                    "file_id": output["file_id"],
                    "filename": output["filename"],
                    **output["extracted_data"]
                })
            return outputs
    
    def get_batch_summary(self, batch_id: str) -> Optional[Dict]:
        """Get batch metadata"""
        with self._lock:
            if batch_id not in self._batches:
                return None
            return self._batches[batch_id]["metadata"].copy()
    
    def get_input_queue(self, batch_id: str) -> List[Dict]:
        """Get input queue status"""
        with self._lock:
            if batch_id not in self._batches:
                return []
            return [f.copy() for f in self._batches[batch_id]["input_queue"]]
    
    def get_output_queue(self, batch_id: str) -> List[Dict]:
        """Get output queue"""
        with self._lock:
            if batch_id not in self._batches:
                return []
            return [f.copy() for f in self._batches[batch_id]["output_queue"]]
    
    def _update_metadata(self, batch_id: str) -> None:
        """Update batch metadata"""
        batch = self._batches[batch_id]
        input_queue = batch["input_queue"]
        
        metadata = {
            "total": len(input_queue),
            "completed": sum(1 for f in input_queue if f["status"] == "completed"),
            "processing": sum(1 for f in input_queue if f["status"] == "processing"),
            "waiting": sum(1 for f in input_queue if f["status"] == "waiting"),
            "failed": sum(1 for f in input_queue if f["status"] == "failed"),
            "current_file_id": batch["metadata"].get("current_file_id")
        }
        
        batch["metadata"] = metadata

# Global instance
queue_manager = QueueManager()