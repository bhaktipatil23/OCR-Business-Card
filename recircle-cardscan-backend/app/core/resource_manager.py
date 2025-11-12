import asyncio
import threading
from typing import Dict, List
from datetime import datetime, timedelta
import queue

class ResourceManager:
    """Manages system resources and ensures fair allocation across users"""
    
    def __init__(self):
        # Global resource limits
        self.max_concurrent_batches = 10  # Max simultaneous users
        self.max_files_per_batch = 300    # Max files per user
        self.max_concurrent_files_per_batch = 5  # Files processed simultaneously per user
        self.max_total_concurrent_files = 20     # Total files processing across all users
        
        # Semaphores for resource control
        self.batch_semaphore = asyncio.Semaphore(self.max_concurrent_batches)
        self.global_file_semaphore = asyncio.Semaphore(self.max_total_concurrent_files)
        
        # Fair scheduling queue
        self.batch_queue = queue.Queue()
        self.active_batches: Dict[str, Dict] = {}
        self.batch_stats: Dict[str, Dict] = {}
        
        # Thread locks
        self.stats_lock = threading.Lock()
        self.queue_lock = threading.Lock()
        
    def validate_batch_size(self, files_count: int) -> bool:
        """Validate if batch size is within limits"""
        return files_count <= self.max_files_per_batch
    
    async def acquire_batch_slot(self, batch_id: str, files_count: int) -> bool:
        """Acquire a slot for batch processing with fair scheduling"""
        if not self.validate_batch_size(files_count):
            return False
        
        # Wait for available batch slot
        await self.batch_semaphore.acquire()
        
        with self.stats_lock:
            self.active_batches[batch_id] = {
                "files_count": files_count,
                "start_time": datetime.now(),
                "processed_files": 0,
                "status": "active"
            }
            
        return True
    
    def release_batch_slot(self, batch_id: str):
        """Release batch slot when processing is complete"""
        with self.stats_lock:
            if batch_id in self.active_batches:
                batch_info = self.active_batches.pop(batch_id)
                self.batch_stats[batch_id] = {
                    **batch_info,
                    "end_time": datetime.now(),
                    "status": "completed"
                }
        
        self.batch_semaphore.release()
    
    async def acquire_file_slot(self, batch_id: str) -> bool:
        """Acquire slot for processing a single file"""
        # Wait for global file processing slot
        await self.global_file_semaphore.acquire()
        
        with self.stats_lock:
            if batch_id in self.active_batches:
                self.active_batches[batch_id]["processed_files"] += 1
        
        return True
    
    def release_file_slot(self, batch_id: str):
        """Release file processing slot"""
        self.global_file_semaphore.release()
    
    def get_system_stats(self) -> Dict:
        """Get current system resource usage statistics"""
        with self.stats_lock:
            return {
                "active_batches": len(self.active_batches),
                "max_concurrent_batches": self.max_concurrent_batches,
                "available_batch_slots": self.batch_semaphore._value,
                "available_file_slots": self.global_file_semaphore._value,
                "active_batch_details": self.active_batches.copy()
            }

# Global resource manager instance
resource_manager = ResourceManager()