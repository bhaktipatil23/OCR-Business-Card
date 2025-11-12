from typing import Dict, List
import threading

class DataStore:
    """In-memory storage for extracted data"""
    
    def __init__(self):
        self._data: Dict[str, List[Dict]] = {}
        self._lock = threading.Lock()
    
    def store_batch_data(self, batch_id: str, records: List[Dict]):
        """Store extracted records for a batch"""
        with self._lock:
            self._data[batch_id] = records
    
    def get_batch_data(self, batch_id: str) -> List[Dict]:
        """Get extracted records for a batch"""
        with self._lock:
            return self._data.get(batch_id, [])
    
    def clear_batch_data(self, batch_id: str):
        """Clear data for a batch"""
        with self._lock:
            if batch_id in self._data:
                del self._data[batch_id]

# Global instance
data_store = DataStore()