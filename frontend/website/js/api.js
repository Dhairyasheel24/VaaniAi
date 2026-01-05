// js/api.js
const API_BASE = "http://127.0.0.1:8000/api/v1";

const API = {
    // 1. Send Audio for STT
    async stt(base64Audio, sourceLang) {
        console.log(`[API] Sending STT request (${sourceLang})...`);
        try {
            const response = await fetch(`${API_BASE}/stt`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    audio_base64: base64Audio,
                    source_lang: sourceLang
                })
            });

            if (!response.ok) {
                const err = await response.json();
                throw new Error(err.detail || "STT Failed");
            }
            return await response.json();
        } catch (e) {
            console.error("[API Error] STT:", e);
            throw e;
        }
    },

    // 2. Translate Text
    async translate(text, sourceLang, targetLang) {
        console.log(`[API] Translating "${text}" to ${targetLang}...`);
        try {
            // NOTE: Using the /translate endpoint (Ensure backend has this)
            // If strictly using the 'ai_client.py' you shared earlier, translation 
            // might be bundled or need a specific endpoint. 
            // Assuming standard REST pattern:
            const response = await fetch(`${API_BASE}/translate`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    text: text,
                    source_lang: sourceLang,
                    target_lang: targetLang
                })
            });

            // Fallback for MVP if endpoint is missing: return same text
            if (response.status === 404) {
                console.warn("[API] /translate endpoint not found. Skipping translation.");
                return { translated_text: text };
            }

            if (!response.ok) throw new Error("Translation Failed");
            return await response.json();
        } catch (e) {
            console.error("[API Error] Translate:", e);
            throw e;
        }
    },

    // 3. Get TTS Audio
    async tts(text, targetLang) {
        console.log(`[API] Requesting TTS (${targetLang})...`);
        try {
            const response = await fetch(`${API_BASE}/tts`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    text: text,
                    target_lang: targetLang
                })
            });

            if (!response.ok) throw new Error("TTS Failed");
            return await response.json();
        } catch (e) {
            console.error("[API Error] TTS:", e);
            throw e;
        }
    }
};