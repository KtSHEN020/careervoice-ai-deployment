from pathlib import Path
from typing import Any, BinaryIO, Protocol

from voice_career_profile_extractor.config import create_openai_client
from voice_career_profile_extractor.transcript import clean_transcript_text

DEFAULT_TRANSCRIPTION_MODEL = "gpt-4o-mini-transcribe"

SUPPORTED_AUDIO_SUFFIXES = {
    ".mp3",
    ".mp4",
    ".mpeg",
    ".mpga",
    ".m4a",
    ".wav",
    ".webm",
}

MAX_AUDIO_FILE_SIZE_BYTES = 25 * 1024 * 1024


class TranscriptionsAPI(Protocol):
    """
    Protocol for an OpenAI-compatible transcription endpoint.
    """

    def create(
        self,
        *,
        model: str,
        file: BinaryIO,
    ) -> Any:
        """Create an audio transcription."""


class AudioAPI(Protocol):
    """
    Protocol for an OpenAI-compatible audio API.
    """

    transcriptions: TranscriptionsAPI


class OpenAIAudioClient(Protocol):
    """
    Protocol for an OpenAI-compatible client with audio support.
    """

    audio: AudioAPI


def transcribe_audio_file(
    audio_path: str | Path,
    *,
    client: OpenAIAudioClient | None = None,
    model: str = DEFAULT_TRANSCRIPTION_MODEL,
) -> str:
    """
    Transcribe an audio file into cleaned text using the OpenAI Audio API.
    """
    path = Path(audio_path)
    _validate_audio_path(path)

    api_client = client or create_openai_client()

    with path.open("rb") as audio_file:
        transcription = api_client.audio.transcriptions.create(
            model=model,
            file=audio_file,
        )

    transcript_text = getattr(transcription, "text", "")

    if not isinstance(transcript_text, str):
        raise RuntimeError("Audio transcription response did not contain text.")

    cleaned_text = clean_transcript_text(transcript_text)

    if not cleaned_text:
        raise RuntimeError("Audio transcription returned empty text.")

    return cleaned_text


def _validate_audio_path(path: Path) -> None:
    if not path.exists():
        raise FileNotFoundError(f"Audio file not found: {path}")

    if not path.is_file():
        raise ValueError(f"Audio path is not a file: {path}")

    if path.suffix.lower() not in SUPPORTED_AUDIO_SUFFIXES:
        supported_formats = ", ".join(sorted(SUPPORTED_AUDIO_SUFFIXES))

        raise ValueError(
            f"Unsupported audio format: {path.suffix or 'no extension'}. "
            f"Supported formats: {supported_formats}"
        )

    if path.stat().st_size >= MAX_AUDIO_FILE_SIZE_BYTES:
        raise ValueError("Audio file must be smaller than 25 MB.")
