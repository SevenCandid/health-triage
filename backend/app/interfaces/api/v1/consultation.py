"""Voice Consultation API Router (Stub).

Placeholder for Phase 2 voice/Gemini consultation endpoints.
See /docs/VoiceSystem.md and /docs/AIArchitecture.md.
"""

import logging
from fastapi import APIRouter

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/consultation", tags=["Consultation & Voice"])


@router.post(
    "/stream",
    summary="Stream Gemini AI enriched consultation (SSE)",
    description=(
        "TODO (Phase 2): Accepts a triage session ID and streams a "
        "Gemini AI empathetic contextual explanation via Server-Sent Events. "
        "See /docs/AIArchitecture.md for system prompt and guardrail specification."
    ),
)
async def stream_consultation() -> dict:
    """Stub endpoint — returns a placeholder until Phase 2 Gemini integration."""
    return {
        "status": "not_implemented",
        "message": (
            "Gemini AI streaming consultation is scheduled for Phase 2. "
            "See /docs/AIArchitecture.md for implementation specification."
        ),
    }


@router.post(
    "/voice/transcribe",
    summary="Transcribe voice audio to text (Whisper STT)",
    description=(
        "TODO (Phase 2): Accepts an audio blob upload and returns a text transcript "
        "using Whisper fine-tuned model for Twi and English. "
        "See /docs/VoiceSystem.md for STT pipeline specification."
    ),
)
async def transcribe_voice() -> dict:
    """Stub endpoint — returns a placeholder until Phase 2 Whisper integration."""
    return {
        "status": "not_implemented",
        "message": (
            "Voice transcription is scheduled for Phase 2. "
            "See /docs/VoiceSystem.md for implementation specification."
        ),
    }
