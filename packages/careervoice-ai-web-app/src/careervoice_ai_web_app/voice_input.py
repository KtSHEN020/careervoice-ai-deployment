"""Browser voice-input models and validation."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

MAX_VOICE_RECORDING_BYTES = 10 * 1024 * 1024

SUPPORTED_VOICE_MEDIA_TYPES = {
    "audio/wav",
}


@dataclass(frozen=True)
class VoiceRecording:
    """Validated browser voice recording."""

    filename: str
    content: bytes
    media_type: str


@dataclass(frozen=True)
class VoiceTranscript:
    """Text produced from one voice recording."""

    text: str


class SupportsVoiceTranscriber(Protocol):
    """Interface for converting a browser recording into text."""

    def transcribe(
        self,
        recording: VoiceRecording,
    ) -> VoiceTranscript:
        """Transcribe one validated voice recording."""


def prepare_voice_recording(
    *,
    filename: str,
    content: bytes,
    media_type: str,
) -> VoiceRecording:
    """Validate browser-recorded audio before transcription."""
    cleaned_filename = filename.strip()

    if not cleaned_filename:
        raise ValueError(
            "The voice recording must have a filename."
        )

    if not isinstance(content, bytes):
        raise ValueError(
            "The voice recording content must be bytes."
        )

    if not content:
        raise ValueError(
            "The voice recording is empty."
        )

    if len(content) > MAX_VOICE_RECORDING_BYTES:
        raise ValueError(
            "The voice recording is too large. "
            "The maximum supported size is 10 MB."
        )

    normalized_media_type = media_type.strip().lower()

    if normalized_media_type not in SUPPORTED_VOICE_MEDIA_TYPES:
        raise ValueError(
            "Unsupported voice recording format. "
            "Browser voice recordings must use WAV audio."
        )

    return VoiceRecording(
        filename=cleaned_filename,
        content=content,
        media_type=normalized_media_type,
    )
