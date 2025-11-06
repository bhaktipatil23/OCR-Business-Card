import asyncio
import requests
import json

# Test script for Gemini Memory Prompts
BASE_URL = "http://localhost:8000"

async def test_memory_prompts():
    """Test the Gemini memory prompt system"""
    
    print("🧪 Testing Gemini Memory Prompt System")
    print("="*50)
    
    # 1. Initialize default prompts
    print("\n1. Initializing default prompts...")
    response = requests.post(f"{BASE_URL}/api/v1/prompts/initialize")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    
    # 2. Store a custom prompt
    print("\n2. Storing custom prompt...")
    custom_prompt = {
        "prompt_id": "enhanced_business_card",
        "content": """
        Extract business card data with ENHANCED accuracy. Focus on:
        1. Multiple phone numbers (mobile + landline)
        2. Complete company names (not abbreviations)
        3. Full addresses with PIN codes
        4. Professional email addresses
        
        Return JSON: [{"name": "...", "phone": "...", "email": "...", "company": "...", "designation": "...", "address": "..."}]
        """,
        "description": "Enhanced business card extraction with focus on completeness"
    }
    
    response = requests.post(f"{BASE_URL}/api/v1/prompts/store", json=custom_prompt)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    
    # 3. List all prompts
    print("\n3. Listing all stored prompts...")
    response = requests.get(f"{BASE_URL}/api/v1/prompts/list")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    
    # 4. Get specific prompt
    print("\n4. Retrieving specific prompt...")
    response = requests.get(f"{BASE_URL}/api/v1/prompts/get/enhanced_business_card")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    
    # 5. Update prompt
    print("\n5. Updating prompt...")
    update_data = {
        "prompt_id": "enhanced_business_card",
        "new_content": """
        ULTRA-ENHANCED business card extraction:
        - Extract ALL visible text
        - Find EVERY phone number (scan 3 times)
        - Get complete addresses with landmarks
        - Include social media handles if present
        
        JSON format: [{"name": "...", "phone": "...", "email": "...", "company": "...", "designation": "...", "address": "..."}]
        """
    }
    
    response = requests.put(f"{BASE_URL}/api/v1/prompts/update", json=update_data)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    
    print("\n✅ Memory prompt system test completed!")
    print("\n📝 Usage Examples:")
    print("- Use custom_prompt_id='enhanced_business_card' in processing")
    print("- Update prompts without code changes")
    print("- Store domain-specific extraction rules")

if __name__ == "__main__":
    asyncio.run(test_memory_prompts())