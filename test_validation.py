import asyncio
import sys
import os

# Add the backend directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'recircle-cardscan-backend'))

from app.services.business_card_validator import BusinessCardValidator

async def test_validation():
    """Test business card validation with a sample image"""
    
    # Find a test image
    test_image_path = None
    
    # Look for test images in the Demo Mul folder
    demo_folder = os.path.join(os.path.dirname(__file__), 'Demo Mul')
    if os.path.exists(demo_folder):
        for file in os.listdir(demo_folder):
            if file.lower().endswith(('.png', '.jpg', '.jpeg')):
                test_image_path = os.path.join(demo_folder, file)
                break
    
    # Look for test images in Test img folder
    if not test_image_path:
        test_folder = os.path.join(os.path.dirname(__file__), 'Test img')
        if os.path.exists(test_folder):
            for file in os.listdir(test_folder):
                if file.lower().endswith(('.png', '.jpg', '.jpeg')):
                    test_image_path = os.path.join(test_folder, file)
                    break
    
    if not test_image_path:
        print("❌ No test images found")
        return
    
    print(f"🔍 Testing validation with: {test_image_path}")
    
    try:
        validator = BusinessCardValidator()
        result = await validator.validate_business_card(test_image_path)
        
        print("\n📋 VALIDATION RESULT:")
        print(f"Is Business Card: {result['is_business_card']}")
        print(f"Confidence: {result['confidence']}")
        print(f"Reasoning: {result['reasoning']}")
        print(f"Information Found: {result['information_found']}")
        print("\n✅ Validation test completed successfully!")
        
    except Exception as e:
        print(f"❌ Validation test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_validation())