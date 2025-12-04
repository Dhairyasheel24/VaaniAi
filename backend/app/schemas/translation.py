from pydantic import Field
from app.schemas.base import BaseSchema

class TranslateRequest(BaseSchema):
    text: str = Field(..., min_length=1, example="Hello")
    source_lang: str = Field(..., pattern=r"^[a-z]{2}(-[A-Z]{2})?$", example="en")
    target_lang: str = Field(..., pattern=r"^[a-z]{2}(-[A-Z]{2})?$", example="hi")

class TranslateResponse(BaseSchema):
    original_text: str
    translated_text: str
    detected_source_lang: str
    target_lang: str