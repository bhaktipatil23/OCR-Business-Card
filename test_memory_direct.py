import asyncio
import sys
import os
sys.path.append('recircle-cardscan-backend')

from app.services.gemini_memory import GeminiMemoryManager, initialize_default_prompts

async def test_direct():
    """Test Gemini memory directly without API server"""
    print("🧪 Testing Gemini Memory Direct")
    print("="*40)
    
    try:
        # Initialize default prompts
        print("\n1. Initializing default prompts...")
        await initialize_default_prompts()
        
        # Test memory manager
        memory = GeminiMemoryManager()
        
        # Store custom prompt
        print("\n2. Storing custom prompt...")
        success = await memory.store_prompt(
            "test_prompt",
            "Extract business card data with focus on phone numbers",
            "Test prompt"
        )
        print(f"Store result: {success}")
        
        # Retrieve prompt
        print("\n3. Retrieving prompt...")
        prompt = await memory.get_prompt("business_card_extraction")
        print(f"Retrieved: {prompt[:100] if prompt else 'None'}...")
        
        print("\n✅ Direct memory test completed!")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_direct())