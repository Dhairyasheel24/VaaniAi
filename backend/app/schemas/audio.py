# FILE: backend/app/schemas/audio.py
from typing import Optional
from pydantic import Field
from app.schemas.base import BaseSchema

class STTRequest(BaseSchema):
    audio_base64: str = Field(..., description="Base64 encoded OPUS audio string")
    source_lang: str = Field(..., pattern=r"^[a-z]{2}(-[A-Z]{2})?$", example="en")

class STTResponse(BaseSchema):
    text: str
    detected_lang: str

class TTSRequest(BaseSchema):
    text: str = Field(..., min_length=1)
    target_lang: str = Field(..., pattern=r"^[a-z]{2}(-[A-Z]{2})?$", example="hi")
    voice: Optional[str] = "default"

class TTSResponse(BaseSchema):
    audio_base64: str = Field(..., description="Base64 encoded audio string")
    duration_ms: int