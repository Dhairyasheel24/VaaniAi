# FILE: backend/app/services/gemini_client.py
import os
import asyncio
import google.generativeai as genai
from google.api_core import exceptions as google_exceptions
from app.core.config import settings
from app.core.logger import get_logger

logger = get_logger(__name__)

class GeminiClient:
    def __init__(self):
        self.api_key = settings.GEMINI_API_KEY
        self.model = None
        
        if not self.api_key or "dummy" in self.api_key:
            logger.warning("⚠️ Gemini API Key is missing/invalid.")
        else:
            genai.configure(api_key=self.api_key)

    async def _get_working_model(self):
        """
        Tries to find a valid model from the list of known Gemini models.
        """
        if self.model: 
            return self.model

        # UPDATED CANDIDATES based on your logs
        candidates = [
            "gemini-2.5-flash",       # Priority 1: Newest Flash
            "gemini-2.0-flash",       # Priority 2: Stable 2.0
            "gemini-2.0-flash-exp",   # Priority 3: Experimental 2.0
            "gemini-1.5-flash",       # Priority 4: Old Flash
            "gemini-pro"              # Priority 5: Standard Pro
        ]

        logger.info("🔍 Auto-detecting available Gemini model...")
        
        try:
            # Get list of models your key can access
            available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
            logger.info(f"📋 Found {len(available_models)} available models.")
        except Exception as e:
            logger.warning(f"Could not list models: {e}. Defaulting to fallback.")
            available_models = []

        # Default fallback if nothing matches
        selected_model_name = "gemini-2.0-flash-exp" 
        
        for candidate in candidates:
            # Check if candidate string appears in any available model name
            # e.g., "gemini-2.5-flash" is inside "models/gemini-2.5-flash"
            if any(candidate in m for m in available_models):
                selected_model_name = candidate
                break
        
        logger.info(f"✅ Selected Model: {selected_model_name}")
        self.model = genai.GenerativeModel(selected_model_name)
        return self.model

    async def translate_text(self, text: str, source_lang: str, target_lang: str) -> dict:
        if not text or not text.strip():
             return self._fallback_response(text, source_lang, target_lang, "Empty input")

        prompt = (
            f"Translate this text from {source_lang} to {target_lang}. "
            f"Return ONLY the translation. Text: {text}"
        )

        try:
            model_instance = await self._get_working_model()
            logger.info(f"🚀 Gemini: Translating '{text[:15]}...' ({source_lang}->{target_lang})")
            
            response = await model_instance.generate_content_async(prompt)
            translated_text = response.text.strip()
            
            return {
                "original_text": text,
                "translated_text": translated_text,
                "detected_source_lang": source_lang,
                "target_lang": target_lang
            }

        except Exception as e:
            logger.error(f"❌ Gemini Error: {e}")
            return self._fallback_response(text, source_lang, target_lang, str(e))

    def _fallback_response(self, text: str, src: str, tgt: str, reason: str) -> dict:
        return {
            "original_text": text,
            "translated_text": f"[Fallback] {text}",
            "detected_source_lang": src,
            "target_lang": tgt
        }

gemini_client = GeminiClient()