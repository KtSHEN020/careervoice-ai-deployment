from pathlib import Path
from typing import BinaryIO

import pytest

from voice_career_profile_extractor import audio_transcriber


class FakeTranscription:
    def __init__(self, text: object) -> None:
        self.text = text


class FakeTranscriptionsAPI:
    def __init__(self, transcript_text: object) -> None:
        self.transcript_text = transcript_text
        self.received_model: str | None = None
        self.received_audio_bytes: bytes | None = None

    def create(
        self,
        *,
        model: str,
        file: BinaryIO,
    ) -> FakeTranscription:
        self.received_model = model
        self.received_audio_bytes = file.read()

        return FakeTranscription(self.transcript_text)


class FakeAudioAPI:
    def __init__(self, transcript_text: object) -> None:
        self.transcriptions = FakeTranscriptionsAPI(transcript_text)


class FakeOpenAIClient:
    def __init__(self, transcript_text: object) -> None:
        self.audio = FakeAudioAPI(transcript_text)


def create_fake_audio_file(
    tmp_path: Path,
    *,
    filename: str = "sample.wav",
    content: bytes = b"fake audio content",
) -> Path:
    audio_file = tmp_path / filename
    audio_file.write_bytes(content)

    return audio_file


def test_transcribe_audio_file_returns_cleaned_text(tmp_path: Path):
    audio_file = create_fake_audio_file(tmp_path)
    client = FakeOpenAIClient(
        "  I want a junior backend role.\n\nI know Python and SQL.  "
    )

    transcript = audio_transcriber.transcribe_audio_file(
        audio_file,
        client=client,
    )

    assert transcript == "I want a junior backend role. I know Python and SQL."


def test_transcribe_audio_file_sends_expected_request(tmp_path: Path):
    audio_file = create_fake_audio_file(
        tmp_path,
        content=b"audio bytes",
    )
    client = FakeOpenAIClient("I know Python.")

    audio_transcriber.transcribe_audio_file(
        audio_file,
        client=client,
    )

    assert (
        client.audio.transcriptions.received_model
        == audio_transcriber.DEFAULT_TRANSCRIPTION_MODEL
    )
    assert client.audio.transcriptions.received_audio_bytes == b"audio bytes"


def test_transcribe_audio_file_uses_custom_model(tmp_path: Path):
    audio_file = create_fake_audio_file(tmp_path)
    client = FakeOpenAIClient("I know Python.")

    audio_transcriber.transcribe_audio_file(
        audio_file,
        client=client,
        model="custom-transcription-model",
    )

    assert client.audio.transcriptions.received_model == "custom-transcription-model"


def test_transcribe_audio_file_rejects_missing_file():
    client = FakeOpenAIClient("I know Python.")

    with pytest.raises(FileNotFoundError, match="Audio file not found"):
        audio_transcriber.transcribe_audio_file(
            "missing.wav",
            client=client,
        )


def test_transcribe_audio_file_rejects_directory(tmp_path: Path):
    client = FakeOpenAIClient("I know Python.")

    with pytest.raises(ValueError, match="Audio path is not a file"):
        audio_transcriber.transcribe_audio_file(
            tmp_path,
            client=client,
        )


def test_transcribe_audio_file_rejects_unsupported_format(tmp_path: Path):
    audio_file = create_fake_audio_file(
        tmp_path,
        filename="sample.txt",
    )
    client = FakeOpenAIClient("I know Python.")

    with pytest.raises(ValueError, match="Unsupported audio format"):
        audio_transcriber.transcribe_audio_file(
            audio_file,
            client=client,
        )


def test_transcribe_audio_file_rejects_oversized_file(
    tmp_path: Path,
    monkeypatch,
):
    audio_file = create_fake_audio_file(
        tmp_path,
        content=b"12345",
    )
    client = FakeOpenAIClient("I know Python.")

    monkeypatch.setattr(
        audio_transcriber,
        "MAX_AUDIO_FILE_SIZE_BYTES",
        5,
    )

    with pytest.raises(ValueError, match="smaller than 25 MB"):
        audio_transcriber.transcribe_audio_file(
            audio_file,
            client=client,
        )


def test_transcribe_audio_file_rejects_empty_transcript(tmp_path: Path):
    audio_file = create_fake_audio_file(tmp_path)
    client = FakeOpenAIClient("   ")

    with pytest.raises(
        RuntimeError,
        match="Audio transcription returned empty text.",
    ):
        audio_transcriber.transcribe_audio_file(
            audio_file,
            client=client,
        )


def test_transcribe_audio_file_rejects_non_string_transcript(tmp_path: Path):
    audio_file = create_fake_audio_file(tmp_path)
    client = FakeOpenAIClient(None)

    with pytest.raises(
        RuntimeError,
        match="Audio transcription response did not contain text.",
    ):
        audio_transcriber.transcribe_audio_file(
            audio_file,
            client=client,
        )
