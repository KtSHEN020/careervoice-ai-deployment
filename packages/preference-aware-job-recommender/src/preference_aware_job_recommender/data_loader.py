from __future__ import annotations

import json
from pathlib import Path
from typing import Any


JsonObject = dict[str, Any]
JobList = list[JsonObject]


def load_json_file(file_path: str | Path) -> Any:
    """
    Load a JSON file and return its parsed content.
    """
    path = Path(file_path)

    try:
        with path.open(encoding="utf-8") as file:
            return json.load(file)
    except json.JSONDecodeError as error:
        raise ValueError(
            f"Invalid JSON in {path}: "
            f"line {error.lineno}, column {error.colno}."
        ) from error


def load_career_profile(file_path: str | Path) -> JsonObject:
    """
    Load a career profile JSON file.
    """
    profile = load_json_file(file_path)

    if not isinstance(profile, dict):
        raise ValueError("Career profile JSON must contain an object.")

    return profile


def load_jobs(file_path: str | Path) -> JobList:
    """
    Load a jobs JSON file.
    """
    jobs = load_json_file(file_path)

    if not isinstance(jobs, list):
        raise ValueError("Jobs JSON must contain a list.")

    if not all(isinstance(job, dict) for job in jobs):
        raise ValueError("Each job in jobs JSON must be an object.")

    return jobs