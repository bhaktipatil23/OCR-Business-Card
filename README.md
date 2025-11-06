# ReCircle OCR Model 2

A full-stack OCR application for processing business cards and documents with AI-powered text extraction.

## Architecture

- **Frontend**: React + TypeScript + Vite (Port 8080)
- **Backend**: FastAPI + Python (Port 8000)
- **OCR**: Google Vision AI integration

## Quick Start

### Option 1: Use the startup script
```bash
# Run both frontend and backend
start.bat
```

### Option 2: Manual startup

#### Backend Setup
```bash
cd recircle-cardscan-backend
pip install -r requirements.txt
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

## API Endpoints

- `POST /api/v1/upload` - Upload files
- `POST /api/v1/process` - Start processing
- `GET /api/v1/status/{batch_id}` - Check processing status
- `GET /api/v1/download/{batch_id}` - Download CSV results

## Features

- ✅ Drag & drop file upload
- ✅ Batch processing (up to 100 files)
- ✅ Real-time processing status
- ✅ CSV export of extracted data
- ✅ Support for images (PNG, JPG, JPEG) and PDFs
- ✅ CORS configured for frontend-backend communication

## Environment Setup

Create `.env` file in `recircle-cardscan-backend/`:
```
GOOGLE_CLOUD_PROJECT_ID=your-project-id
GOOGLE_APPLICATION_CREDENTIALS=path/to/credentials.json
```

## Usage

1. Start both servers using `start.bat`
2. Open http://localhost:8080 in your browser
3. Upload image folders or individual files
4. Wait for processing to complete
5. Download the CSV results

## File Structure

```
OCR Model 2/
├── frontend/                 # React frontend
│   ├── src/
│   │   ├── services/api.ts  # Backend API integration
│   │   ├── pages/Index.tsx  # Main upload page
│   │   └── components/      # UI components
│   └── package.json
├── recircle-cardscan-backend/ # FastAPI backend
│   ├── app/
│   │   ├── main.py         # FastAPI app with CORS
│   │   ├── routers/        # API endpoints
│   │   └── services/       # OCR processing
│   └── requirements.txt
└── start.bat               # Startup script
```