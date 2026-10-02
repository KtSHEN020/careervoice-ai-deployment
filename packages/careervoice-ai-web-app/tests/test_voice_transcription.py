from __future__ import annotations

from pathlib import Path

import pytest

from careervoice_ai_web_app.voice_input import (
    VoiceRecording,
)
from careervoice_ai_web_app.voice_transcription import (
    Repo1VoiceTranscriber,
)


def _recording() -> VoiceRecording:
    return VoiceRecording(
        filename="career-voice.wav",
        content=b"fake-browser-audio",
        media_type="audio/wav",
    )

def _recording_with_media_type(
    *,
    filename: str,
    media_type: str,
) -> VoiceRecording:
    return VoiceRecording(
        filename=filename,
        content=b"fake-browser-audio",
        media_type=media_type,
    )

def test_repo1_voice_transcriber_passes_wav_to_repo1() -> None:
    received_path: Path | None = None
    received_bytes: bytes | None = None

    def fake_transcribe(
        audio_path: str | Path,
    ) -> str:
        nonlocal received_path
        nonlocal received_bytes

        path = Path(audio_path)

        received_path = path
        received_bytes = path.read_bytes()

        return (
            "  I want a junior backend role.\n\n"
            "I know Python and SQL.  "
        )

    transcriber = Repo1VoiceTranscriber(
        transcribe_fn=fake_transcribe,
    )

    result = transcriber.transcribe(
        _recording()
    )

    assert received_path is not None
    assert received_path.suffix == ".wav"

    assert (
        received_bytes
        == b"fake-browser-audio"
    )

    assert result.text == (
        "I want a junior backend role. "
        "I know Python and SQL."
    )


def test_repo1_voice_transcriber_removes_temporary_file() -> None:
    received_path: Path | None = None

    def fake_transcribe(
        audio_path: str | Path,
    ) -> str:
        nonlocal received_path

        received_path = Path(audio_path)

        assert received_path.is_file()

        return "I know Python."

    transcriber = Repo1VoiceTranscriber(
        transcribe_fn=fake_transcribe,
    )

    transcriber.transcribe(
        _recording()
    )

    assert received_path is not None
    assert not received_path.exists()


def test_repo1_voice_transcriber_rejects_empty_transcript() -> None:
    def fake_transcribe(
        _audio_path: str | Path,
    ) -> str:
        return "   "

    transcriber = Repo1VoiceTranscriber(
        transcribe_fn=fake_transcribe,
    )

    with pytest.raises(
        ValueError,
        match="No speech could be transcribed",
    ):
        transcriber.transcribe(
            _recording()
        )


def test_repo1_voice_transcriber_converts_repo1_failure() -> None:
    def fake_transcribe(
        _audio_path: str | Path,
    ) -> str:
        raise RuntimeError(
            "simulated transcription failure"
        )

    transcriber = Repo1VoiceTranscriber(
        transcribe_fn=fake_transcribe,
    )

    with pytest.raises(
        ValueError,
        match="Voice transcription could not be completed",
    ):
        transcriber.transcribe(
            _recording()
        )


def test_repo1_voice_transcriber_uses_webm_suffix() -> None:
    received_path: Path | None = None

    def fake_transcribe(
        audio_path: str | Path,
    ) -> str:
        nonlocal received_path

        received_path = Path(audio_path)

        return "I know Python."

    transcriber = Repo1VoiceTranscriber(
        transcribe_fn=fake_transcribe,
    )

    transcriber.transcribe(
        _recording_with_media_type(
            filename="career-voice.webm",
            media_type="audio/webm",
        )
    )

    assert received_path is not None
    assert received_path.suffix == ".webm"


def test_repo1_voice_transcriber_uses_mp4_suffix() -> None:
    received_path: Path | None = None

    def fake_transcribe(
        audio_path: str | Path,
    ) -> str:
        nonlocal received_path

        received_path = Path(audio_path)

        return "I know Python."

    transcriber = Repo1VoiceTranscriber(
        transcribe_fn=fake_transcribe,
    )

    transcriber.transcribe(
        _recording_with_media_type(
            filename="career-voice.mp4",
            media_type="audio/mp4",
        )
    )

    assert received_path is not None
    assert received_path.suffix == ".mp4"


def test_repo1_voice_transcriber_accepts_media_type_parameters() -> None:
    received_path: Path | None = None

    def fake_transcribe(
        audio_path: str | Path,
    ) -> str:
        nonlocal received_path

        received_path = Path(audio_path)

        return "I know Python."

    transcriber = Repo1VoiceTranscriber(
        transcribe_fn=fake_transcribe,
    )

    transcriber.transcribe(
        _recording_with_media_type(
            filename="career-voice.webm",
            media_type="audio/webm;codecs=opus",
        )
    )

    assert received_path is not None
    assert received_path.suffix == ".webm"