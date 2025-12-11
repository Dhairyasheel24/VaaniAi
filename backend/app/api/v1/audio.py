# FILE: backend/app/api/v1/audio.py
from fastapi import APIRouter, HTTPException
from app.schemas.audio import STTRequest, STTResponse, TTSRequest, TTSResponse
from app.services.ai_client import ai_client  # <--- UPDATED IMPORT
from app.core.logger import get_logger

router = APIRouter()
logger = get_logger(__name__)

@router.post("/stt", response_model=STTResponse)
async def speech_to_text(request: STTRequest):
    """
    Converts Speech to Text using Local Whisper Model via AIClient.
    """
    logger.info(f"API: STT Request ({request.source_lang})")
    try:
        result = await ai_client.stt.transcribe(
            audio_base64=request.audio_base64,
            source_lang=request.source_lang
        )
        return STTResponse(**result)
    except Exception as e:
        logger.error(f"API: STT Failed: {str(e)}")
        raise HTTPException(status_code=500, detail="STT processing failed")

@router.post("/tts", response_model=TTSResponse)
async def text_to_speech(request: TTSRequest):
    """
    Converts Text to Speech using Microsoft Edge TTS via AIClient.
    """
    logger.info(f"API: TTS Request ({request.target_lang})")
    try:
        result = await ai_client.tts.synthesize(
            text=request.text,
            target_lang=request.target_lang,
            voice=request.voice
        )
        return TTSResponse(**result)
    except Exception as e:
        logger.error(f"API: TTS Failed: {str(e)}")
        raise HTTPException(status_code=500, detail="TTS generation failed")