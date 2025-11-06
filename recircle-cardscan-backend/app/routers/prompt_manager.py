from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.services.gemini_memory import GeminiMemoryManager, initialize_default_prompts
from typing import Optional

router = APIRouter(prefix="/api/v1/prompts", tags=["prompts"])

class PromptRequest(BaseModel):
    prompt_id: str
    content: str
    description: Optional[str] = ""

class PromptUpdateRequest(BaseModel):
    prompt_id: str
    new_content: str

@router.post("/store")
async def store_prompt(request: PromptRequest):
    """Store a new prompt in Gemini memory"""
    memory = GeminiMemoryManager()
    success = await memory.store_prompt(request.prompt_id, request.content, request.description)
    
    if success:
        return {"message": f"Prompt '{request.prompt_id}' stored successfully"}
    else:
        raise HTTPException(status_code=500, detail="Failed to store prompt")

@router.get("/get/{prompt_id}")
async def get_prompt(prompt_id: str):
    """Retrieve a stored prompt"""
    memory = GeminiMemoryManager()
    prompt = await memory.get_prompt(prompt_id)
    
    if prompt:
        return {"prompt_id": prompt_id, "content": prompt}
    else:
        raise HTTPException(status_code=404, detail=f"Prompt '{prompt_id}' not found")

@router.put("/update")
async def update_prompt(request: PromptUpdateRequest):
    """Update an existing prompt"""
    memory = GeminiMemoryManager()
    success = await memory.update_prompt(request.prompt_id, request.new_content)
    
    if success:
        return {"message": f"Prompt '{request.prompt_id}' updated successfully"}
    else:
        raise HTTPException(status_code=500, detail="Failed to update prompt")

@router.get("/list")
async def list_prompts():
    """List all stored prompts"""
    memory = GeminiMemoryManager()
    prompts = await memory.list_stored_prompts()
    return prompts

@router.post("/initialize")
async def initialize_prompts():
    """Initialize default prompts in Gemini memory"""
    try:
        await initialize_default_prompts()
        return {"message": "Default prompts initialized successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to initialize prompts: {str(e)}")