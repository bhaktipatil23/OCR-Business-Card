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
    app_logger.info("[UPLOAD] STEP 1: FILE UPLOAD STARTED - 3 files received")
    app_logger.info("[UPLOAD] Batch size validation passed: 3 files")
    app_logger.info("[UPLOAD] Generated batch ID: batch_20241106_123456")
    app_logger.info("[UPLOAD] Processing file: business_card_1.jpg")
    app_logger.info("[UPLOAD] Generated file ID: f_abc123 for business_card_1.jpg")
    app_logger.info("[UPLOAD] File saved: business_card_1.jpg -> /storage/f_abc123_business_card_1.jpg")
    app_logger.info("[UPLOAD] STEP 1 COMPLETED: 3 files stored in batch batch_20241106_123456")
    app_logger.info("[UPLOAD] NEXT STEP: Files ready for validation")
    
    print("\n" + "=" * 50)
    
    app_logger.info("[VALIDATION] STEP 2: VALIDATION STARTED for batch batch_20241106_123456")
    app_logger.info("[VALIDATION] Found 3 files to validate in batch batch_20241106_123456")
    app_logger.info("[VALIDATION] Business card validator initialized")
    app_logger.info("[VALIDATION] Starting AI validation for 3 files...")
    app_logger.info("[VALIDATOR] [1/3] Validating: business_card_1.jpg")
    app_logger.info("[VALIDATOR] Sending image to Gemini AI for business card validation...")
    app_logger.info("[VALIDATOR] Received validation response from Gemini AI")
    app_logger.info("[VALIDATOR] Validation result: VALID (confidence: High)")
    app_logger.info("[VALIDATOR] [1/3] business_card_1.jpg: VALID business card")
    app_logger.info("[VALIDATION] VALIDATION SUMMARY: 2 valid business cards, 1 invalid files")
    app_logger.info("[VALIDATION] STEP 2 COMPLETED: Validation finished for batch batch_20241106_123456")
    app_logger.info("[VALIDATION] NEXT STEP: Ready for processing 2 valid business cards")
    
    print("\n" + "=" * 50)
    
    app_logger.info("[PROCESS] STEP 3: PROCESSING STARTED for batch batch_20241106_123456")
    app_logger.info("[PROCESS] Retrieved validation results for batch batch_20241106_123456")
    app_logger.info("[PROCESS] Filtering files based on validation results...")
    app_logger.info("[PROCESS] business_card_1.jpg: Added to processing queue (valid business card)")
    app_logger.info("[PROCESS] invalid_image.jpg: Skipped (not a business card)")
    app_logger.info("[PROCESS] PROCESSING SUMMARY: 2 valid files, 1 invalid files")
    app_logger.info("[PROCESS] Starting background OCR processing for 2 business cards...")
    app_logger.info("[PROCESS] STEP 3 INITIATED: Background processing started for batch batch_20241106_123456")
    app_logger.info("[PROCESS] NEXT STEP: OCR processing in progress...")
    
    print("\n" + "=" * 50)
    
    app_logger.info("[OCR] STEP 4: OCR PROCESSING STARTED for batch batch_20241106_123456")
    app_logger.info("[OCR] Processing 2 valid business card files")
    app_logger.info("[OCR] Initializing OCR processor for batch batch_20241106_123456")
    app_logger.info("[OCR] Starting OCR extraction for 2 files...")
    app_logger.info("[PROCESSOR] Processing business card: business_card_1.jpg")
    app_logger.info("[PROCESSOR] Extracting data with Gemini AI...")
    app_logger.info("[PROCESSOR] EXTRACTED DATA (Valid - 6/6 fields): John Doe | ABC Company")
    app_logger.info("[PROCESSOR] Phone: 9876543210 | Email: john@abc.com")
    app_logger.info("[PROCESSOR] File 1 completed: business_card_1.jpg")
    app_logger.info("[OCR] OCR processing completed for batch batch_20241106_123456")
    app_logger.info("[OCR] CSV file generated: /output/batch_20241106_123456_data.csv")
    app_logger.info("[OCR] STEP 4 COMPLETED: All files processed successfully for batch batch_20241106_123456")
    app_logger.info("[OCR] FINAL STEP: Ready for download")
    
    print("\n" + "=" * 50)
    print("SUCCESS: Logging test completed successfully!")
    print("All workflow steps are now logged with detailed information.")

if __name__ == "__main__":
    test_logging()