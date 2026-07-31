import wave
from collections.abc import Callable
from pathlib import Path
from typing import Any

import pytest

from voice_career_profile_extractor.audio_recorder import (
    AUDIO_DTYPE,
    DEFAULT_CHANNELS,
    DEFAULT_SAMPLE_RATE,
    record_microphone_to_wav,
)


class FakeRawInputStream:
    def __init__(
        self,
        *,
        callback: Callable[[Any, int, Any, Any], None],
        audio_chunks: list[bytes],
    ) -> None:
        self.callback = callback
        self.audio_chunks = audio_chunks
        self.entered = False
        self.exited = False

    def __enter__(self) -> "FakeRawInputStream":
        self.entered = True

        for audio_chunk in self.audio_chunks:
            self.callback(audio_chunk, 0, None, None)

        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: Any,
    ) -> None:
        self.exited = True


class FakeSoundDeviceBackend:
    def __init__(self, audio_chunks: list[bytes]) -> None:
        self.audio_chunks = audio_chunks
        self.received_arguments: dict[str, Any] = {}
        self.stream: FakeRawInputStream | None = None

    def RawInputStream(
        self,
        *,
        samplerate: int,
        channels: int,
        dtype: str,
        callback: Callable[[Any, int, Any, Any], None],
    ) -> FakeRawInputStream:
        self.received_arguments = {
            "samplerate": samplerate,
            "channels": channels,
            "dtype": dtype,
        }

        self.stream = FakeRawInputStream(
            callback=callback,
            audio_chunks=self.audio_chunks,
        )

        return self.stream


def create_input_fn(received_prompts: list[str]) -> Callable[[str], str]:
    def fake_input(prompt: str) -> str:
        received_prompts.append(prompt)
        return ""

    return fake_input


def test_record_microphone_to_wav_saves_valid_wav_file(tmp_path: Path):
    output_path = tmp_path / "recording.wav"
    backend = FakeSoundDeviceBackend([b"\x01\x02", b"\x03\x04"])
    received_prompts: list[str] = []

    saved_path = record_microphone_to_wav(
        output_path,
        input_fn=create_input_fn(received_prompts),
        sounddevice_backend=backend,
    )

    assert saved_path == output_path
    assert output_path.exists()
    assert received_prompts == [
        "Press Enter to start recording.",
        "Recording... Press Enter to stop.",
    ]

    with wave.open(str(output_path), "rb") as wav_file:
        assert wav_file.getnchannels() == DEFAULT_CHANNELS
        assert wav_file.getsampwidth() == 2
        assert wav_file.getframerate() == DEFAULT_SAMPLE_RATE
        assert wav_file.readframes(wav_file.getnframes()) == b"\x01\x02\x03\x04"


def test_record_microphone_to_wav_uses_expected_stream_options(tmp_path: Path):
    output_path = tmp_path / "recording.wav"
    backend = FakeSoundDeviceBackend([b"\x01\x02"])

    record_microphone_to_wav(
        output_path,
        input_fn=lambda _: "",
        sounddevice_backend=backend,
    )

    assert backend.received_arguments == {
        "samplerate": DEFAULT_SAMPLE_RATE,
        "channels": DEFAULT_CHANNELS,
        "dtype": AUDIO_DTYPE,
    }
    assert backend.stream is not None
    assert backend.stream.entered is True
    assert backend.stream.exited is True


def test_record_microphone_to_wav_creates_parent_directory(tmp_path: Path):
    output_path = tmp_path / "outputs" / "recording.wav"
    backend = FakeSoundDeviceBackend([b"\x01\x02"])

    saved_path = record_microphone_to_wav(
        output_path,
        input_fn=lambda _: "",
        sounddevice_backend=backend,
    )

    assert saved_path == output_path
    assert output_path.exists()


def test_record_microphone_to_wav_rejects_non_wav_output(tmp_path: Path):
    output_path = tmp_path / "recording.mp3"
    backend = FakeSoundDeviceBackend([b"\x01\x02"])

    with pytest.raises(ValueError, match="must use the .wav format"):
        record_microphone_to_wav(
            output_path,
            input_fn=lambda _: "",
            sounddevice_backend=backend,
        )


def test_record_microphone_to_wav_rejects_invalid_sample_rate(tmp_path: Path):
    output_path = tmp_path / "recording.wav"
    backend = FakeSoundDeviceBackend([b"\x01\x02"])

    with pytest.raises(ValueError, match="Sample rate must be greater than zero"):
        record_microphone_to_wav(
            output_path,
            sample_rate=0,
            input_fn=lambda _: "",
            sounddevice_backend=backend,
        )


def test_record_microphone_to_wav_rejects_invalid_channel_count(tmp_path: Path):
    output_path = tmp_path / "recording.wav"
    backend = FakeSoundDeviceBackend([b"\x01\x02"])

    with pytest.raises(ValueError, match="Channel count must be greater than zero"):
        record_microphone_to_wav(
            output_path,
            channels=0,
            input_fn=lambda _: "",
            sounddevice_backend=backend,
        )


def test_record_microphone_to_wav_rejects_empty_recording(tmp_path: Path):
    output_path = tmp_path / "recording.wav"
    backend = FakeSoundDeviceBackend([])

    with pytest.raises(RuntimeError, match="No microphone audio was recorded"):
        record_microphone_to_wav(
            output_path,
            input_fn=lambda _: "",
            sounddevice_backend=backend,
        )
