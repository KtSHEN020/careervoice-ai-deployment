from pathlib import Path

import pytest

from voice_career_profile_extractor import (
    clean_transcript_text,
    load_transcript,
)


def test_clean_transcript_text_removes_empty_lines_and_extra_spaces():
    raw_text = """
        I am looking for a junior software developer role.

        I know Python, SQL, and Git.
    """

    cleaned_text = clean_transcript_text(raw_text)

    assert (
        cleaned_text == "I am looking for a junior software developer role. "
        "I know Python, SQL, and Git."
    )


def test_load_transcript_reads_and_cleans_text_file(tmp_path: Path):
    transcript_file = tmp_path / "sample_transcript.txt"
    transcript_file.write_text(
        """
        I am looking for a junior software developer role.

        I prefer backend or data-related roles.
        """,
        encoding="utf-8",
    )

    loaded_text = load_transcript(transcript_file)

    assert (
        loaded_text == "I am looking for a junior software developer role. "
        "I prefer backend or data-related roles."
    )


def test_load_transcript_raises_error_for_missing_file():
    with pytest.raises(FileNotFoundError):
        load_transcript("missing_file.txt")


def test_load_transcript_raises_error_for_empty_file(tmp_path: Path):
    transcript_file = tmp_path / "empty.txt"
    transcript_file.write_text("   \n\n   ", encoding="utf-8")

    with pytest.raises(ValueError, match="Transcript file is empty."):
        load_transcript(transcript_file)


def test_load_transcript_raises_error_for_directory(tmp_path: Path):
    with pytest.raises(ValueError, match="Transcript path is not a file"):
        load_transcript(tmp_path)
