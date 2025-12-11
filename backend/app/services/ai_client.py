# FILE: backend/app/services/ai_client.py
import os
import base64
import asyncio
import tempfile
from concurrent.futures import ThreadPoolExecutor

# External Libraries
from groq import AsyncGroq
import edge_tts
import whisper
from app.core.config import settings
from app.core.logger import get_logger

logger = get_logger(__name__)

# --- 1. Groq Translation Service ---
class GroqTranslationService:
    def __init__(self):
        self.api_key = settings.GROQ_API_KEY
        
        if not self.api_key:
            logger.warning("⚠️ GROQ_API_KEY is missing. Translation will fail.")
            self.client = None
        else:
            self.client = AsyncGroq(api_key=self.api_key)
        
        # UPDATED: Use the new stable model
        self.model = "llama-3.3-70b-versatile" 

    async def translate(self, text: str, source_lang: str, target_lang: str) -> dict:
        if not self.client:
             logger.error("Groq Client not initialized (Missing API Key)")
             return self._fallback(text, source_lang, target_lang)

        prompt = (
            f"Translate the following text from {source_lang} to {target_lang}. "
            f"Output ONLY the translated text. No notes, no explanations.\n\n"
            f"Text: {text}"
        )

        try:
            logger.info(f"Groq: Translating via {self.model}...")
            completion = await self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=1024,
            )
            translated_text = completion.choices[0].message.content.strip()
            
            return {
                "original_text": text,
                "translated_text": translated_text,
                "detected_source_lang": source_lang,
                "target_lang": target_lang
            }
        except Exception as e:
            logger.error(f"Groq Translation Error: {e}")
            return self._fallback(text, source_lang, target_lang)

    def _fallback(self, text, src, tgt):
        return {
            "original_text": text,
            "translated_text": f"[Error] {text}",
            "detected_source_lang": src,
            "target_lang": tgt
        }

# --- 2. Whisper STT Service (Local) ---
class WhisperSTTService:
    def __init__(self):
        self.model = None
        self.executor = ThreadPoolExecutor(max_workers=1)

    def _load_model(self):
        if not self.model:
            logger.info("Whisper: Loading 'tiny' model (CPU friendly)...")
            self.model = whisper.load_model("tiny")

    async def transcribe(self, audio_base64: str, source_lang: str) -> dict:
        loop = asyncio.get_event_loop()
        
        # FIX: Handle header/padding issues
        try:
            if "," in audio_base64:
                audio_base64 = audio_base64.split(",")[1]
            
            # Add padding if missing
            missing_padding = len(audio_base64) % 4
            if missing_padding:
                audio_base64 += '=' * (4 - missing_padding)
                
            audio_bytes = base64.b64decode(audio_base64)
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
                tmp.write(audio_bytes)
                tmp_path = tmp.name
        except Exception as e:
            logger.error(f"Audio Decode Error: {e}")
            return {"text": "", "detected_lang": "error"}

        try:
            if not self.model:
                await loop.run_in_executor(self.executor, self._load_model)

            logger.info("Whisper: Transcribing...")
            lang_code = source_lang.split('-')[0] if source_lang else None
            
            def _run_whisper():
                return self.model.transcribe(tmp_path, language=lang_code, fp16=False)

            result = await loop.run_in_executor(self.executor, _run_whisper)
            text = result.get("text", "").strip()

            return {
                "text": text,
                "detected_lang": source_lang
            }
        except Exception as e:
            logger.error(f"Whisper STT Error: {e}")
            return {"text": "[STT Error]", "detected_lang": source_lang}
        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)

# --- 3. Edge TTS Service ---
class EdgeTTSService:
    VOICE_MAP = {
        "en": "en-US-AriaNeural",
        "hi": "hi-IN-SwaraNeural",
        "es": "es-ES-ElviraNeural",
        "fr": "fr-FR-DeniseNeural",
        "de": "de-DE-KatjaNeural",
        "default": "en-US-AriaNeural"
    }

    async def synthesize(self, text: str, target_lang: str, voice: str = "default") -> dict:
        selected_voice = self.VOICE_MAP.get(target_lang.split('-')[0], self.VOICE_MAP["default"])
        
        logger.info(f"EdgeTTS: Synthesizing '{text[:15]}...' with {selected_voice}")
        
        try:
            communicate = edge_tts.Communicate(text, selected_voice)
            audio_data = b""
            async for chunk in communicate.stream():
                if chunk["type"] == "audio":
                    audio_data += chunk["data"]

            b64_audio = base64.b64encode(audio_data).decode("utf-8")
            duration_ms = len(audio_data) / 16
            
            return {
                "audio_base64": b64_audio,
                "duration_ms": int(duration_ms)
            }
        except Exception as e:
            logger.error(f"EdgeTTS Error: {e}")
            return {"audio_base64": "", "duration_ms": 0}

# --- 4. Unified AI Client ---
class AIClient:
    def __init__(self):
        self.translation = GroqTranslationService()
        self.stt = WhisperSTTService()
        self.tts = EdgeTTSService()

ai_client = AIClient()