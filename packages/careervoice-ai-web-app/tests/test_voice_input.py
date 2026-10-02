from __future__ import annotations

import pytest

from careervoice_ai_web_app.voice_input import (
    MAX_VOICE_RECORDING_BYTES,
    prepare_voice_recording,
    voice_media_type_suffix,
)


def test_prepare_voice_recording_accepts_wav_audio() -> None:
    recording = prepare_voice_recording(
        filename="career-voice.wav",
        content=b"fake-wav-content",
        media_type="audio/wav",
    )

    assert recording.filename == "career-voice.wav"
    assert recording.content == b"fake-wav-content"
    assert recording.media_type == "audio/wav"


def test_prepare_voice_recording_accepts_webm_audio() -> None:
    recording = prepare_voice_recording(
        filename="career-voice.webm",
        content=b"fake-webm-content",
        media_type="audio/webm;codecs=opus",
    )

    assert recording.media_type == "audio/webm"


def test_prepare_voice_recording_accepts_mp4_audio() -> None:
    recording = prepare_voice_recording(
        filename="career-voice.mp4",
        content=b"fake-mp4-content",
        media_type="audio/mp4",
    )

    assert recording.media_type == "audio/mp4"


def test_prepare_voice_recording_normalizes_media_type() -> None:
    recording = prepare_voice_recording(
        filename="career-voice.wav",
        content=b"fake-wav-content",
        media_type=" AUDIO/WAV ",
    )

    assert recording.media_type == "audio/wav"


def test_voice_media_type_suffix_maps_browser_formats() -> None:
    assert (
        voice_media_type_suffix(
            "audio/wav"
        )
        == ".wav"
    )

    assert (
        voice_media_type_suffix(
            "audio/webm;codecs=opus"
        )
        == ".webm"
    )

    assert (
        voice_media_type_suffix(
            "audio/mp4"
        )
        == ".mp4"
    )


def test_empty_voice_recording_is_rejected() -> None:
    with pytest.raises(
        ValueError,
        match="voice recording is empty",
    ):
        prepare_voice_recording(
            filename="career-voice.wav",
            content=b"",
            media_type="audio/wav",
        )


def test_unsupported_voice_format_is_rejected() -> None:
    with pytest.raises(
        ValueError,
        match="Unsupported voice recording format",
    ):
        prepare_voice_recording(
            filename="career-voice.ogg",
            content=b"fake-audio",
            media_type="audio/ogg",
        )


def test_large_voice_recording_is_rejected() -> None:
    with pytest.raises(
        ValueError,
        match="maximum supported size is 10 MB",
    ):
        prepare_voice_recording(
            filename="career-voice.wav",
            content=b"x" * (
                MAX_VOICE_RECORDING_BYTES + 1
            ),
            media_type="audio/wav",
        )