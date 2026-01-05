# FILE: backend/app/api/v1/audio.py
from fastapi import APIRouter, HTTPException
from app.schemas.audio import STTRequest, STTResponse, TTSRequest, TTSResponse
from app.services.ai_client import ai_client
from app.core.logger import get_logger

router = APIRouter()
logger = get_logger(__name__)

@router.post("/stt", response_model=STTResponse)
async def speech_to_text(request: STTRequest):
    """
    Real-time Speech-to-Text using local Whisper model.
    Accepts Base64 audio (WAV/MP3/Opus/WebM).
    """
    logger.info(f"API: STT Request ({request.source_lang})")
    try:
        result = await ai_client.stt.transcribe(
            audio_base64=request.audio_base64,
            source_lang=request.source_lang
        )
        return STTResponse(**result)
    
    except ValueError as e:
        # Invalid Base64 or empty input
        logger.warning(f"API: STT Bad Request: {str(e)}")
        raise HTTPException(status_code=422, detail=str(e))
        
    except Exception as e:
        logger.error(f"API: STT Failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error during transcription")

@router.post("/tts", response_model=TTSResponse)
async def text_to_speech(request: TTSRequest):
    """
    Real-time Text-to-Speech using gTTS.
    Returns Base64 MP3 and duration.
    """
    logger.info(f"API: TTS Request ({request.target_lang})")
    try:
        # gTTS does not support 'voice', so we do not pass it.
        result = await ai_client.tts.synthesize(
            text=request.text,
            target_lang=request.target_lang
        )
        return TTSResponse(**result)
        
    except ValueError as e:
        # Invalid text or language code
        logger.warning(f"API: TTS Bad Request: {str(e)}")
        raise HTTPException(status_code=422, detail=str(e))
        
    except Exception as e:
        logger.error(f"API: TTS Failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error during synthesis")