from fastapi import APIRouter
from models.model import TranslationRequest
from service.translation import perform_translation

router = APIRouter()

@router.post("/translate")
async def translate(request : TranslationRequest):
    result = perform_translation(request.text,request.lang)
    return {"translated_text" : result}