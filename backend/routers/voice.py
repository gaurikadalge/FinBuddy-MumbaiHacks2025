# backend/routers/voice.py

import base64
import uuid
from pathlib import Path
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from backend.services.ai_orchestrator import AIOrchestrator
from backend.utils.logger import logger

router = APIRouter(prefix="/api/voice", tags=["Voice Processing"])

VOICE_DIR = Path("voice_uploads")
VOICE_DIR.mkdir(parents=True, exist_ok=True)


def get_orchestrator():
    return AIOrchestrator()


# ---------------------------------------------------------
# Request Model
# ---------------------------------------------------------
class VoiceUpload(BaseModel):
    audio_base64: str = Field(..., description="Base64-encoded audio input.")
    model_config = {"from_attributes": True}


# ---------------------------------------------------------
# 1️⃣ Process Voice Input
# ---------------------------------------------------------
@router.post("/process")
async def process_voice(req: VoiceUpload):
    try:
        if not req.audio_base64.strip():
            raise HTTPException(status_code=400, detail="audio_base64 is required")

        logger.info("🎤 Received voice data, decoding audio...")

        # --------------------------------------------------
        # Decode Base64 → Save as temp WAV for debugging
        # --------------------------------------------------
        try:
            audio_bytes = base64.b64decode(req.audio_base64)
        except Exception:
            raise HTTPException(status_code=400, detail="Invalid base64 audio string")

        # Save WAV file
        filename = f"voice_{uuid.uuid4().hex[:10]}.wav"
        filepath = VOICE_DIR / filename

        with open(filepath, "wb") as f:
            f.write(audio_bytes)

        logger.info(f"🎧 Saved decoded audio to: {filepath}")

        # --------------------------------------------------
        # AI Orchestrator STT + Parsing + AI Pipeline
        # --------------------------------------------------
        orchestrator = get_orchestrator()
        result = await orchestrator.process_voice(req.audio_base64)

        if not result.get("success"):
            raise HTTPException(status_code=500, detail="Voice processing failed")

        # --------------------------------------------------
        # Unified response format
        # --------------------------------------------------
        return {
            "success": True,
            "text": result.get("text"),  # unified key
            "category": result.get("category"),
            "ai_insight": result.get("ai_insight"),
            "parsed_data": result.get("parsed_data", {}),
            "provider": result.get("provider_used", "unknown"),
            "saved_file": str(filepath)
        }

    except Exception as e:
        logger.error(f"❌ Voice processing error: {e}")
        raise HTTPException(status_code=500, detail="Voice processing failed")
