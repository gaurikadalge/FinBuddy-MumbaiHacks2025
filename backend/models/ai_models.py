# backend/models/ai_models.py

from pydantic import BaseModel, Field, field_validator
from typing import Optional
import re


# ------------------------------------------------------------
# AI TEXT REQUEST MODEL
# ------------------------------------------------------------
class AIRequest(BaseModel):
    prompt: str = Field(..., description="User's message or instruction for the AI model.")
    max_tokens: int = Field(256, ge=1, le=4096)
    provider: Optional[str] = Field(
        None,
        description="AI provider (openai, gemini, cohere, groq). If None → auto-select."
    )

    model_config = {"from_attributes": True}

    @field_validator("provider")
    def validate_provider(cls, v):
        if v is None:
            return v
        allowed = {"openai", "gemini", "cohere", "groq"}
        if v.lower() not in allowed:
            raise ValueError(f"Invalid provider '{v}'. Allowed: {allowed}")
        return v.lower()


# ------------------------------------------------------------
# AI TEXT RESPONSE MODEL
# ------------------------------------------------------------
class AIResponse(BaseModel):
    text: str = Field(..., description="Generated text output from the AI provider.")
    provider: str = Field(..., description="Provider used for generation.")
    success: bool = Field(True, description="Whether the AI request succeeded.")

    model_config = {"from_attributes": True}


# ------------------------------------------------------------
# VOICE REQUEST MODEL
# ------------------------------------------------------------
class VoiceRequest(BaseModel):
    audio_data: str = Field(
        ...,
        description="Base64-encoded audio input from the user."
    )
    language: str = Field(
        "hi-IN",
        description="Language code for speech-to-text recognition."
    )

    model_config = {"from_attributes": True}

    @field_validator("audio_data")
    def validate_base64(cls, v):
        """
        Light base64 format validation to prevent invalid audio payloads.
        """
        if not re.match(r"^[A-Za-z0-9+/=]+$", v[:50]):
            raise ValueError("audio_data does not look like valid base64-encoded text.")
        return v


# ------------------------------------------------------------
# VOICE RESPONSE MODEL
# ------------------------------------------------------------
class VoiceResponse(BaseModel):
    text: str = Field(..., description="Recognized text from audio input.")
    success: bool = Field(True, description="Whether transcription succeeded.")

    model_config = {"from_attributes": True}
