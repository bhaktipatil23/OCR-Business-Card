from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import upload, process, download, pdf_preview_simple, vcf_export, prompt_manager, extracted_data, save_data, process_single, websocket_router
from app.config import settings
import os
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create storage directories
os.makedirs(settings.TEMP_STORAGE_PATH, exist_ok=True)
os.makedirs(settings.OUTPUT_CSV_PATH, exist_ok=True)

# Database initialization removed - using direct MySQL connections in routers

app = FastAPI(
    title="ReCircle CardScan API",
    description="Business Card OCR System with Vision AI",
    version="1.0.0"
)

# CORS middleware for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(upload.router)
app.include_router(process.router)
app.include_router(process_single.router)
app.include_router(websocket_router.router)
app.include_router(download.router)
app.include_router(pdf_preview_simple.router, prefix="/api/v1")
app.include_router(vcf_export.router, prefix="/api/v1")
app.include_router(prompt_manager.router)
app.include_router(extracted_data.router)
# Removed field_update and email_lookup routers due to database dependency issues
app.include_router(save_data.router)

@app.get("/")
async def root():
    return {
        "message": "ReCircle CardScan API",
        "version": "1.0.0",
        "status": "running",
        "database": "MySQL integrated"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)