import sys
import os

# Add the backend directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'recircle-cardscan-backend'))

from app.utils.logger import app_logger

def test_logging():
    """Test the logging functionality"""
    
    print("Testing OCR Workflow Logging System")
    print("=" * 50)
    
    # Test different log levels
    app_logger.info("📤 STEP 1: FILE UPLOAD STARTED - 3 files received")
    app_logger.info("✅ Batch size validation passed: 3 files")
    app_logger.info("🆔 Generated batch ID: batch_20241106_123456")
    app_logger.info("📁 Processing file: business_card_1.jpg")
    app_logger.info("🆔 Generated file ID: f_abc123 for business_card_1.jpg")
    app_logger.info("💾 File saved: business_card_1.jpg -> /storage/f_abc123_business_card_1.jpg")
    app_logger.info("📊 STEP 1 COMPLETED: 3 files stored in batch batch_20241106_123456")
    app_logger.info("🔄 NEXT STEP: Files ready for validation")
    
    print("\n" + "=" * 50)
    
    app_logger.info("🔍 STEP 2: VALIDATION STARTED for batch batch_20241106_123456")
    app_logger.info("📁 Found 3 files to validate in batch batch_20241106_123456")
    app_logger.info("🤖 Business card validator initialized")
    app_logger.info("🔍 Starting AI validation for 3 files...")
    app_logger.info("🔍 [1/3] Validating: business_card_1.jpg")
    app_logger.info("🤖 Sending image to Gemini AI for business card validation...")
    app_logger.info("✅ Received validation response from Gemini AI")
    app_logger.info("📄 Validation result: VALID (confidence: High)")
    app_logger.info("✅ [1/3] business_card_1.jpg: VALID business card")
    app_logger.info("📈 VALIDATION SUMMARY: 2 valid business cards, 1 invalid files")
    app_logger.info("🎉 STEP 2 COMPLETED: Validation finished for batch batch_20241106_123456")
    app_logger.info("🔄 NEXT STEP: Ready for processing 2 valid business cards")
    
    print("\n" + "=" * 50)
    
    app_logger.info("🚀 STEP 3: PROCESSING STARTED for batch batch_20241106_123456")
    app_logger.info("📁 Retrieved validation results for batch batch_20241106_123456")
    app_logger.info("🔍 Filtering files based on validation results...")
    app_logger.info("✅ business_card_1.jpg: Added to processing queue (valid business card)")
    app_logger.info("⏭️ invalid_image.jpg: Skipped (not a business card)")
    app_logger.info("📈 PROCESSING SUMMARY: 2 valid files, 1 invalid files")
    app_logger.info("🚀 Starting background OCR processing for 2 business cards...")
    app_logger.info("🎉 STEP 3 INITIATED: Background processing started for batch batch_20241106_123456")
    app_logger.info("🔄 NEXT STEP: OCR processing in progress...")
    
    print("\n" + "=" * 50)
    
    app_logger.info("🔄 STEP 4: OCR PROCESSING STARTED for batch batch_20241106_123456")
    app_logger.info("📁 Processing 2 valid business card files")
    app_logger.info("🤖 Initializing OCR processor for batch batch_20241106_123456")
    app_logger.info("🚀 Starting OCR extraction for 2 files...")
    app_logger.info("🔄 Processing business card: business_card_1.jpg")
    app_logger.info("🤖 Extracting data with Gemini AI...")
    app_logger.info("✅ EXTRACTED DATA (Valid - 6/6 fields): John Doe | ABC Company")
    app_logger.info("   📞 Phone: 9876543210 | 📧 Email: john@abc.com")
    app_logger.info("✅ File 1/2 completed: business_card_1.jpg")
    app_logger.info("✅ OCR processing completed for batch batch_20241106_123456")
    app_logger.info("📄 CSV file generated: /output/batch_20241106_123456_data.csv")
    app_logger.info("🎉 STEP 4 COMPLETED: All files processed successfully for batch batch_20241106_123456")
    app_logger.info("🔄 FINAL STEP: Ready for download")
    
    print("\n" + "=" * 50)
    print("✅ Logging test completed successfully!")
    print("All workflow steps are now logged with detailed information.")

if __name__ == "__main__":
    test_logging()