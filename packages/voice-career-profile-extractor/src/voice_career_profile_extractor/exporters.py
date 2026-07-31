import json
from pathlib import Path

from voice_career_profile_extractor.models import CareerProfile


def profile_to_json(profile: CareerProfile, *, indent: int = 2) -> str:
    """
    Convert a career profile into a formatted JSON string.
    """
    return json.dumps(profile.to_dict(), indent=indent, ensure_ascii=False)


def save_profile_json(
    profile: CareerProfile,
    output_path: str | Path,
    *,
    indent: int = 2,
) -> Path:
    """
    Save a career profile as a JSON file.
    """
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    json_text = profile_to_json(profile, indent=indent)
    path.write_text(f"{json_text}\n", encoding="utf-8")

    return path
