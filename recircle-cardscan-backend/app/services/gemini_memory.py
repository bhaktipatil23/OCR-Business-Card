import google.generativeai as genai
from typing import Dict, Optional
import json
import os
from app.config import settings
from pathlib import Path

class GeminiMemoryManager:
    def __init__(self):
        genai.configure(api_key=settings.GEMINI_API_KEY)
        self.model = genai.GenerativeModel('gemini-2.0-flash-exp')
        self.prompts_file = Path("prompts_storage.json")
        self._load_prompts()
        
    def _load_prompts(self):
        """Load prompts from local file"""
        if self.prompts_file.exists():
            with open(self.prompts_file, 'r') as f:
                self.stored_prompts = json.load(f)
        else:
            self.stored_prompts = {}
    
    def _save_prompts(self):
        """Save prompts to local file"""
        with open(self.prompts_file, 'w') as f:
            json.dump(self.stored_prompts, f, indent=2)
        
    async def store_prompt(self, prompt_id: str, prompt_content: str, description: str = "") -> bool:
        """Store a prompt locally"""
        try:
            self.stored_prompts[prompt_id] = {
                "content": prompt_content,
                "description": description
            }
            self._save_prompts()
            print(f"✅ Stored prompt '{prompt_id}' locally")
            return True
            
        except Exception as e:
            print(f"❌ Failed to store prompt '{prompt_id}': {e}")
            return False
    
    async def get_prompt(self, prompt_id: str) -> Optional[str]:
        """Retrieve a stored prompt locally"""
        try:
            if prompt_id in self.stored_prompts:
                return self.stored_prompts[prompt_id]["content"]
            return None
            
        except Exception as e:
            print(f"❌ Failed to retrieve prompt '{prompt_id}': {e}")
            return None
    
    async def update_prompt(self, prompt_id: str, new_content: str) -> bool:
        """Update an existing prompt locally"""
        try:
            if prompt_id in self.stored_prompts:
                self.stored_prompts[prompt_id]["content"] = new_content
                self._save_prompts()
                print(f"✅ Updated prompt '{prompt_id}'")
                return True
            return False
            
        except Exception as e:
            print(f"❌ Failed to update prompt '{prompt_id}': {e}")
            return False
    
    async def list_stored_prompts(self) -> Dict:
        """List all stored prompts"""
        try:
            prompt_list = []
            for prompt_id, data in self.stored_prompts.items():
                prompt_list.append({
                    "id": prompt_id,
                    "description": data.get("description", ""),
                    "content_preview": data["content"][:100] + "..."
                })
            return {"prompts": prompt_list}
            
        except Exception as e:
            print(f"❌ Failed to list prompts: {e}")
            return {"prompts": "Error retrieving prompts"}

# Initialize default prompts
async def initialize_default_prompts():
    """Store default prompts in Gemini memory"""
    memory = GeminiMemoryManager()
    
    # Business card extraction prompt
    business_card_prompt = """
    Extract business card information from this image and return ONLY valid JSON.
    
    EXTRACTION RULES:
    1. Extract: name, phone, email, company, designation, address
    2. Multiple phones/emails: comma-separated
    3. Remove +91 from phones >10 digits starting with 91
    4. Use "N/A" for missing fields
    5. Return array of objects for multiple cards
    
    JSON FORMAT:
    [{"name": "value", "phone": "value", "email": "value", "company": "value", "designation": "value", "address": "value"}]
    """
    

    
    # Store prompts
    await memory.store_prompt("business_card_extraction", business_card_prompt, "Extract business card data as JSON")
    
    print("✅ Default prompts initialized in Gemini memory")