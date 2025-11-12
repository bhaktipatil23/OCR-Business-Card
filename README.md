# OCR Business Card Application

A full-stack OCR application for processing business cards with AI-powered validation and text extraction.

## Features

- ✅ Business card validation using AI
- ✅ Drag & drop file upload (up to 300 files, 20MB total)
- ✅ Batch processing with real-time status
- ✅ CSV export of extracted data
- ✅ Support for images (PNG, JPG, JPEG) and PDFs
- ✅ Comprehensive logging system

## Architecture

- **Frontend**: React + TypeScript + Vite (Port 8080)
- **Backend**: FastAPI + Python (Port 8000)
- **AI**: Google Gemini AI for validation and OCR

## Quick Start

### Prerequisites
- Python 3.8+
- Node.js 16+
- Google Gemini API key

### Backend Setup
```bash
cd recircle-cardscan-backend
pip install -r requirements.txt
cp .env.example .env
# Add your GEMINI_API_KEY to .env file
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

## Usage

1. Start both servers
2. Open http://localhost:8080
3. Upload business card images
4. System validates files automatically
5. Valid business cards are processed for OCR
6. Download CSV results

## API Endpoints

- `POST /api/v1/upload` - Upload files
- `POST /api/v1/validate/{batch_id}` - Validate business cards
- `POST /api/v1/process` - Start OCR processing
- `GET /api/v1/status/{batch_id}` - Check processing status
- `GET /api/v1/download/{batch_id}` - Download CSV results

## Environment Variables

```env
GEMINI_API_KEY=your-gemini-api-key-here
MAX_FILES_PER_BATCH=300
ALLOWED_EXTENSIONS=jpg,jpeg,png,pdf
```

## File Limits

- **File Count**: Maximum 300 files per batch
- **Total Size**: Maximum 20MB total for all files combined
- **File Types**: JPG, JPEG, PNG, PDF

## Workflow

1. **Upload**: Files uploaded to Python list
2. **Validation**: AI checks if files are business cards
3. **Processing**: Valid cards processed for OCR
4. **Export**: Results saved to CSV

## License

MIT License