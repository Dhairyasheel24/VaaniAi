# FILE: backend/app/services/ai_client.py
import os
import base64
import tempfile
import asyncio
import shutil
from groq import AsyncGroq
from gtts import gTTS
from pydub import AudioSegment
from app.core.config import settings
from app.core.logger import get_logger

logger = get_logger(__name__)

# --- 1. Groq Translation Service ---
class GroqTranslationService:
    def __init__(self):
        self.api_key = settings.GROQ_API_KEY
        self.client = AsyncGroq(api_key=self.api_key) if self.api_key else None
        # Llama 3 is great, but we need to control its personality
        self.model = "llama-3.3-70b-versatile"

    async def translate(self, text: str, source_lang: str, target_lang: str) -> dict:
        if not self.client:
             return {"translated_text": "[Error: No API Key]", "original_text": text}

        # FIX 1: Robust System Prompt for Indian Languages
        # We tell it to ignore script inconsistencies and just work.
        prompt = (
            f"You are a professional translator specializing in Indian languages. "
            f"Translate the following text from {source_lang} to {target_lang}. "
            f"Rules:\n"
            f"1. Output ONLY the translated text.\n"
            f"2. Do NOT provide notes, explanations, or disclaimers.\n"
            f"3. If the input seems to be a name or proper noun, transliterate it directly.\n"
            f"4. Do NOT complain about the input language script. Just translate it best-effort.\n\n"
            f"Text: {text}"
        )

        try:
            completion = await self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=1024,
            )
            translated_text = completion.choices[0].message.content.strip()
            
            # Safety cleanup (sometimes LLMs still add quotes)
            translated_text = translated_text.replace('"', '').replace("Here is the translation:", "").strip()

            return {
                "original_text": text,
                "translated_text": translated_text,
                "detected_source_lang": source_lang,
                "target_lang": target_lang
            }
        except Exception as e:
            logger.error(f"Groq Translation Error: {e}")
            return {
                "original_text": text,
                "translated_text": f"[Error] {text}",
                "detected_source_lang": source_lang,
                "target_lang": target_lang
            }

# --- 2. Groq STT Service ---
class GroqSTTService:
    def __init__(self):
        self.api_key = settings.GROQ_API_KEY
        self.client = AsyncGroq(api_key=self.api_key) if self.api_key else None
        self.model = "whisper-large-v3" 

    async def transcribe(self, audio_base64: str, source_lang: str) -> dict:
        if not self.client:
            logger.error("Groq Client missing for STT")
            return {"text": "", "detected_lang": "error"}

        tmp_path = None
        try:
            # 1. Decode Base64
            if "," in audio_base64:
                audio_base64 = audio_base64.split(",")[1]
            
            if not audio_base64:
                return {"text": "", "detected_lang": "silent"}

            audio_bytes = base64.b64decode(audio_base64)
            logger.info(f"Groq STT: Received {len(audio_bytes)} bytes")

            # 2. Save as .webm
            with tempfile.NamedTemporaryFile(suffix=".webm", delete=False) as tmp:
                tmp.write(audio_bytes)
                tmp_path = tmp.name

            # 3. Send to Groq API
            with open(tmp_path, "rb") as file_obj:
                # FIX 2: Force Language Detection
                # We pass the 'language' param so Whisper doesn't guess "Urdu" for "Hindi"
                transcription = await self.client.audio.transcriptions.create(
                    file=(tmp_path, file_obj.read()),
                    model=self.model,
                    response_format="json",
                    language=source_lang # <--- THIS FORCES CORRECT LANGUAGE
                )
            
            text = transcription.text.strip()
            logger.info(f"Groq STT Result ({source_lang}): '{text}'")

            if not text:
                return {"text": "", "detected_lang": "silent"}

            return {
                "text": text,
                "detected_lang": source_lang
            }

        except Exception as e:
            logger.error(f"Groq STT Error: {e}")
            return {"text": "", "detected_lang": "error"}
        finally:
            if tmp_path and os.path.exists(tmp_path):
                try:
                    os.remove(tmp_path)
                except Exception:
                    pass

# --- 3. Google TTS Service (gTTS) ---
class GTTSService:
    async def synthesize(self, text: str, target_lang: str) -> dict:
        temp_path = None
        try:
            if not text or not text.strip():
                raise ValueError("Text input cannot be empty")

            lang_code = target_lang.split('-')[0]
            tld = "com"
            if target_lang in ["en-UK", "en-GB"]: tld = "co.uk"
            elif target_lang == "en-IN": tld = "co.in"

            logger.info(f"gTTS: Synthesizing '{text[:15]}...' in {lang_code}")

            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp_file:
                temp_path = tmp_file.name

            loop = asyncio.get_event_loop()
            
            def _run_gtts():
                # gTTS is robust for Indian languages
                tts = gTTS(text=text, lang=lang_code, tld=tld, slow=False)
                tts.save(temp_path)

            await loop.run_in_executor(None, _run_gtts)

            audio = AudioSegment.from_file(temp_path)
            duration_ms = len(audio)

            with open(temp_path, "rb") as f:
                audio_base64 = base64.b64encode(f.read()).decode("utf-8")

            return {
                "audio_base64": audio_base64,
                "duration_ms": int(duration_ms)
            }

        except Exception as e:
            logger.error(f"TTS Error (gTTS): {e}")
            return {"audio_base64": "", "duration_ms": 0}
        finally:
            if temp_path and os.path.exists(temp_path):
                try: os.remove(temp_path)
                except: pass

# --- 4. Unified AI Client ---
class AIClient:
    def __init__(self):
        self.translation = GroqTranslationService()
        self.stt = GroqSTTService()
        self.tts = GTTSService()

ai_client = AIClient()