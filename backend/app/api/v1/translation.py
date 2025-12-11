# FILE: backend/app/api/v1/translation.py
from fastapi import APIRouter, HTTPException
from app.schemas.translation import TranslateRequest, TranslateResponse
from app.services.ai_client import ai_client  # <--- UPDATED IMPORT
from app.core.logger import get_logger

router = APIRouter()
logger = get_logger(__name__)

@router.post("/translate", response_model=TranslateResponse)
async def translate_text_endpoint(request: TranslateRequest):
    """
    Translates text using Groq API via AIClient.
    """
    logger.info(f"API: Translation Request '{request.text[:15]}...' ({request.source_lang}->{request.target_lang})")
    
    try:
        result = await ai_client.translation.translate(
            text=request.text,
            source_lang=request.source_lang,
            target_lang=request.target_lang
        )
        return TranslateResponse(**result)
    except Exception as e:
        logger.error(f"API Translation Failed: {e}")
        raise HTTPException(status_code=500, detail="Translation failed")