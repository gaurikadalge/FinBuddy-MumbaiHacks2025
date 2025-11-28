// frontend/assets/js/voice.js — HYBRID H2 MODE (FINAL)

class VoiceRecorder {
    constructor() {
        this.isRecording = false;
        this.mediaRecorder = null;
        this.audioChunks = [];
        this.stream = null;
    }

    async toggleRecording() {
        if (!this.isRecording) await this.startRecording();
        else await this.stopRecording();
    }

    // ----------------------------------------------------------
    // START RECORDING
    // ----------------------------------------------------------
    async startRecording() {
        try {
            if (!navigator.mediaDevices) {
                throw new Error("Browser does not support voice recording.");
            }

            this.stream = await navigator.mediaDevices.getUserMedia({
                audio: { echoCancellation: true, noiseSuppression: true }
            });

            const mimeType =
                MediaRecorder.isTypeSupported("audio/webm")
                    ? "audio/webm"
                    : "";

            this.mediaRecorder = new MediaRecorder(this.stream, { mimeType });

            this.audioChunks = [];
            this.mediaRecorder.ondataavailable = e => {
                if (e.data.size > 0) this.audioChunks.push(e.data);
            };

            this.mediaRecorder.onstop = () => this.processRecording();

            this.mediaRecorder.start();
            this.isRecording = true;

            this.updateButton(true);

            setTimeout(() => {
                if (this.isRecording) this.stopRecording();
            }, 7000);
        } catch (err) {
            console.error(err);
            this.showVoiceError("Microphone access denied.");
        }
    }

    // ----------------------------------------------------------
    // STOP RECORDING
    // ----------------------------------------------------------
    async stopRecording() {
        if (!this.mediaRecorder || !this.isRecording) return;

        try {
            this.mediaRecorder.stop();
        } catch (err) { }

        this.isRecording = false;
        this.updateButton(false);

        if (this.stream) {
            this.stream.getTracks().forEach(t => t.stop());
        }
    }

    // ----------------------------------------------------------
    // SEND AUDIO TO BACKEND FOR STT → NLP → CHAT PIPELINE
    // ----------------------------------------------------------
    async processRecording() {
        try {
            window.chat.addMessage("🎤 Processing voice…", "user");
            window.chat.showTyping();

            const blob = new Blob(this.audioChunks, {
                type: this.mediaRecorder.mimeType || "audio/webm"
            });

            const base64 = await this.blobToBase64(blob);

            const res = await fetch("/api/voice/process", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    audio_base64: base64,
                    user_id: window.chat.userId
                })
            });

            const data = await res.json().catch(() => ({}));

            window.chat.hideTyping();

            if (data.success && data.text) {
                await window.chat.processVoiceText(data.text);

                // Show Voice Semantics
                if (data.voice_semantics && data.voice_semantics.tags.length > 0) {
                    const tags = data.voice_semantics.tags.join(", ");
                    const sentiment = data.voice_semantics.sentiment;

                    window.chat.addMessage(
                        `🧠 <strong>Voice Analysis:</strong> Detected ${tags} (${sentiment} tone)`,
                        "bot"
                    );
                }
            } else {
                window.chat.addMessage(
                    "Voice could not be recognized. Try again.",
                    "bot",
                    "error"
                );
            }
        } catch (err) {
            console.error(err);
            window.chat.hideTyping();
            window.chat.addMessage(
                "Voice processing error. Please type instead.",
                "bot",
                "error"
            );
        }
    }

    blobToBase64(blob) {
        return new Promise(resolve => {
            const reader = new FileReader();
            reader.onloadend = () => resolve(reader.result.split(",")[1]);
            reader.readAsDataURL(blob);
        });
    }

    // ----------------------------------------------------------
    // UI BUTTON
    // ----------------------------------------------------------
    updateButton(recording) {
        const btn = document.getElementById("voiceBtn");
        if (!btn) return;

        if (recording) {
            btn.classList.add("recording", "btn-danger");
            btn.innerHTML = `<i class="fas fa-stop"></i>`;
        } else {
            btn.classList.remove("recording", "btn-danger");
            btn.innerHTML = `<i class="fas fa-microphone"></i>`;
        }
    }

    showVoiceError(msg) {
        window.chat.addMessage(`🎤 ${msg}`, "bot", "error");
    }
}

document.addEventListener("DOMContentLoaded", () => {
    window.voiceRecorder = new VoiceRecorder();
});
