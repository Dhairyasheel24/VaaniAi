from fastapi import APIRouter, HTTPException
from app.schemas.translation import TranslateRequest, TranslateResponse
from app.services.gemini_client import gemini_client
from app.core.logger import get_logger

router = APIRouter()
logger = get_logger(__name__)

@router.post("/translate", response_model=TranslateResponse)
async def translate_text_endpoint(request: TranslateRequest):
    """
    Real-time translation endpoint using Gemini.
    """
    logger.info(f"API: Request '{request.text[:20]}...' ({request.source_lang}->{request.target_lang})")
    
    # Call Service
    result = await gemini_client.translate_text(
        text=request.text,
        source_lang=request.source_lang,
        target_lang=request.target_lang
    )
    
    return TranslateResponse(
        original_text=result["original_text"],
        translated_text=result["translated_text"],
        detected_source_lang=result["detected_source_lang"],
        target_lang=result["target_lang"]
    )