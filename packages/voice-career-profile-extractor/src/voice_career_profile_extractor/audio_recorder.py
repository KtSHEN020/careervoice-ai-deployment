import wave
from collections.abc import Callable
from pathlib import Path
from queue import Empty, SimpleQueue
from typing import Any, Protocol

DEFAULT_SAMPLE_RATE = 16_000
DEFAULT_CHANNELS = 1
SAMPLE_WIDTH_BYTES = 2
AUDIO_DTYPE = "int16"


class RawInputStream(Protocol):
    """
    Protocol for a sounddevice-compatible raw input stream.
    """

    def __enter__(self) -> "RawInputStream":
        """
        Start the audio stream.
        """

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: Any,
    ) -> None:
        """
        Stop and close the audio stream.
        """


class SoundDeviceBackend(Protocol):
    """
    Protocol for a sounddevice-compatible recording backend.
    """

    def RawInputStream(
        self,
        *,
        samplerate: int,
        channels: int,
        dtype: str,
        callback: Callable[[Any, int, Any, Any], None],
    ) -> RawInputStream:
        """
        Create a raw microphone input stream.
        """


def record_microphone_to_wav(
    output_path: str | Path,
    *,
    sample_rate: int = DEFAULT_SAMPLE_RATE,
    channels: int = DEFAULT_CHANNELS,
    input_fn: Callable[[str], str] = input,
    sounddevice_backend: SoundDeviceBackend | None = None,
) -> Path:
    """
    Record microphone audio and save it as a WAV file.
    """
    path = Path(output_path)
    _validate_recording_options(path, sample_rate=sample_rate, channels=channels)

    backend = sounddevice_backend or _load_sounddevice_backend()
    audio_chunks: SimpleQueue[bytes] = SimpleQueue()

    def audio_callback(
        input_data: Any,
        _frames: int,
        _time_info: Any,
        _status: Any,
    ) -> None:
        audio_chunks.put(bytes(input_data))

    input_fn("Press Enter to start recording.")

    with backend.RawInputStream(
        samplerate=sample_rate,
        channels=channels,
        dtype=AUDIO_DTYPE,
        callback=audio_callback,
    ):
        input_fn("Recording... Press Enter to stop.")

    audio_bytes = _collect_audio_chunks(audio_chunks)

    if not audio_bytes:
        raise RuntimeError("No microphone audio was recorded.")

    path.parent.mkdir(parents=True, exist_ok=True)
    _write_wav_file(
        path,
        audio_bytes,
        sample_rate=sample_rate,
        channels=channels,
    )

    return path


def _load_sounddevice_backend() -> SoundDeviceBackend:
    try:
        import sounddevice
    except ImportError as exc:
        raise RuntimeError(
            "Microphone recording requires the optional 'voice' dependency. "
            "Install it with: uv sync --extra voice"
        ) from exc

    return sounddevice


def _validate_recording_options(
    path: Path,
    *,
    sample_rate: int,
    channels: int,
) -> None:
    if path.suffix.lower() != ".wav":
        raise ValueError("Microphone recording output must use the .wav format.")

    if sample_rate <= 0:
        raise ValueError("Sample rate must be greater than zero.")

    if channels <= 0:
        raise ValueError("Channel count must be greater than zero.")


def _collect_audio_chunks(audio_chunks: SimpleQueue[bytes]) -> bytes:
    chunks = []

    while True:
        try:
            chunks.append(audio_chunks.get_nowait())
        except Empty:
            break

    return b"".join(chunks)


def _write_wav_file(
    path: Path,
    audio_bytes: bytes,
    *,
    sample_rate: int,
    channels: int,
) -> None:
    with wave.open(str(path), "wb") as wav_file:
        wav_file.setnchannels(channels)
        wav_file.setsampwidth(SAMPLE_WIDTH_BYTES)
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(audio_bytes)
