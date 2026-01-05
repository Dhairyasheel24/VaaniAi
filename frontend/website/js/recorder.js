// js/recorder.js
class VoiceRecorder {
    constructor() {
        this.mediaRecorder = null;
        this.audioChunks = [];
    }

    // Initialize and Start Recording
    async start() {
        if (!navigator.mediaDevices) {
            throw new Error("Microphone access not supported in this browser.");
        }

        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        
        // Use 'audio/webm' (Standard for Chrome/Firefox)
        // Backend's Groq/Whisper MUST support WebM (We ensured this in previous steps)
        const mimeType = 'audio/webm'; 
        
        this.mediaRecorder = new MediaRecorder(stream, { mimeType });
        this.audioChunks = [];

        this.mediaRecorder.ondataavailable = (event) => {
            if (event.data.size > 0) {
                this.audioChunks.push(event.data);
            }
        };

        this.mediaRecorder.start();
        console.log("[Recorder] Started");
    }

    // Stop and return Base64 String
    stop() {
        return new Promise((resolve, reject) => {
            if (!this.mediaRecorder) return reject("Recorder not initialized");

            this.mediaRecorder.onstop = () => {
                const audioBlob = new Blob(this.audioChunks, { type: 'audio/webm' });
                const reader = new FileReader();
                
                reader.readAsDataURL(audioBlob);
                reader.onloadend = () => {
                    // Result is "data:audio/webm;base64,....." -> We need split
                    const base64String = reader.result.split(',')[1];
                    resolve(base64String);
                };
                reader.onerror = (error) => reject(error);
            };

            this.mediaRecorder.stop();
            // Important: Turn off the mic light on the browser tab
            this.mediaRecorder.stream.getTracks().forEach(track => track.stop());
            console.log("[Recorder] Stopped");
        });
    }
}