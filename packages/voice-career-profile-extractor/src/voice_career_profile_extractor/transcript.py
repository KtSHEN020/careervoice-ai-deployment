from pathlib import Path


def clean_transcript_text(text: str) -> str:
    """
    Clean transcript text by trimming lines and removing empty lines.
    """
    cleaned_lines = [line.strip() for line in text.splitlines() if line.strip()]
    return " ".join(cleaned_lines)


def load_transcript(path: str | Path) -> str:
    """
    Load and clean transcript text from a text file.
    """
    transcript_path = Path(path)

    if not transcript_path.exists():
        raise FileNotFoundError(f"Transcript file not found: {transcript_path}")

    if not transcript_path.is_file():
        raise ValueError(f"Transcript path is not a file: {transcript_path}")

    text = transcript_path.read_text(encoding="utf-8")
    cleaned_text = clean_transcript_text(text)

    if not cleaned_text:
        raise ValueError("Transcript file is empty.")

    return cleaned_text
