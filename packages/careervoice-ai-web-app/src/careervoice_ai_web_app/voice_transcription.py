"""Adapter for transcribing browser audio through Repo 1."""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path
from tempfile import TemporaryDirectory

from voice_career_profile_extractor import (
    clean_transcript_text,
    transcribe_audio_file,
)

from careervoice_ai_web_app.voice_input import (
    VoiceRecording,
    VoiceTranscript,
    voice_media_type_suffix,
)

TranscribeAudioFile = Callable[[str | Path], str]


class Repo1VoiceTranscriber:
    """Transcribe browser recordings using Repo 1's public API."""

    def __init__(
        self,
        *,
        transcribe_fn: TranscribeAudioFile = transcribe_audio_file,
    ) -> None:
        self._transcribe_fn = transcribe_fn

    def transcribe(
        self,
        recording: VoiceRecording,
    ) -> VoiceTranscript:
        """Transcribe one browser voice recording."""
        try:
            with TemporaryDirectory(
                prefix="careervoice-voice-"
            ) as temporary_directory:
                audio_suffix = voice_media_type_suffix(
                    recording.media_type
                )

                audio_path = (
                    Path(temporary_directory)
                    / f"browser-recording{audio_suffix}"
                )

                audio_path.write_bytes(
                    recording.content
                )

                transcript_text = self._transcribe_fn(
                    audio_path
                )

        except (OSError, RuntimeError, ValueError) as error:
            raise ValueError(
                "Voice transcription could not be completed."
            ) from error

        cleaned_text = clean_transcript_text(
            transcript_text
        )

        if not cleaned_text:
            raise ValueError(
                "No speech could be transcribed from the recording."
            )

        return VoiceTranscript(
            text=cleaned_text,
        )
