from fastapi import APIRouter, HTTPException
from models.model import TextInput
from service.translation import summarize_text, kr_summarize_text

router = APIRouter()

@router.post("/en-summarize/")
async def summarize(input: TextInput):
    """영어 텍스트를 요약하고 번역하는 API."""
    text = input.text
    if not text:
        raise HTTPException(status_code=400, detail="Input text cannot be empty.")
    
    return await summarize_text(text)

@router.post("/kr-summarize/")
async def kr_summarize(input: TextInput):
    """한국어 텍스트를 요약하는 API."""
    text = input.text.strip()
    if not text:
        raise HTTPException(status_code=400, detail="Input text cannot be empty.")

    return await kr_summarize_text(text)
