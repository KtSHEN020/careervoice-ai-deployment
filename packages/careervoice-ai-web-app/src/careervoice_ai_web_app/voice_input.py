"""Browser voice-input models and validation."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

MAX_VOICE_RECORDING_BYTES = 10 * 1024 * 1024

VOICE_MEDIA_TYPE_SUFFIXES = {
    "audio/wav": ".wav",
    "audio/x-wav": ".wav",
    "audio/webm": ".webm",
    "audio/mp4": ".mp4",
    "audio/mpeg": ".mp3",
    "audio/m4a": ".m4a",
    "audio/x-m4a": ".m4a",
}

SUPPORTED_VOICE_MEDIA_TYPES = set(
    VOICE_MEDIA_TYPE_SUFFIXES
)


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
        ...


def normalize_voice_media_type(
    media_type: str,
) -> str:
    """Return a normalized browser audio media type."""
    return (
        media_type
        .strip()
        .lower()
        .split(";", maxsplit=1)[0]
        .strip()
    )


def voice_media_type_suffix(
    media_type: str,
) -> str:
    """Return the audio-file suffix for one supported media type."""
    normalized_media_type = (
        normalize_voice_media_type(
            media_type
        )
    )

    try:
        return VOICE_MEDIA_TYPE_SUFFIXES[
            normalized_media_type
        ]
    except KeyError as error:
        raise ValueError(
            "Unsupported voice recording format."
        ) from error


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

    normalized_media_type = (
        normalize_voice_media_type(
            media_type
        )
    )

    if (
        normalized_media_type
        not in SUPPORTED_VOICE_MEDIA_TYPES
    ):
        raise ValueError(
            "Unsupported voice recording format. "
            "Supported browser audio includes "
            "WAV, WebM, MP4/M4A, and MP3."
        )

    return VoiceRecording(
        filename=cleaned_filename,
        content=content,
        media_type=normalized_media_type,
    )