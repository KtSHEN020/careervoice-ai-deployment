from __future__ import annotations

import json
from pathlib import Path

from careervoice_ai_orchestrator.models import (
    WorkflowConfig,
    normalize_job_queries,
)


def load_career_profile(profile_path: Path) -> dict[str, object]:
    """
    Load and validate a career profile JSON object.
    """
    try:
        profile_text = profile_path.read_text(encoding="utf-8")
    except FileNotFoundError as error:
        raise ValueError(
            f"Career profile file was not found: {profile_path}"
        ) from error
    except OSError as error:
        raise ValueError(
            f"Career profile file could not be read: {profile_path}"
        ) from error

    try:
        profile_data = json.loads(profile_text)
    except json.JSONDecodeError as error:
        raise ValueError(
            f"Career profile contains invalid JSON: {profile_path}"
        ) from error

    if not isinstance(profile_data, dict):
        raise ValueError(
            f"Career profile must contain a JSON object: {profile_path}"
        )

    return profile_data


def extract_target_roles(profile_data: dict[str, object]) -> tuple[str, ...]:
    """
    Extract clean, unique target roles from career-profile data.

    Missing target_roles and an empty target_roles list are treated as having
    no available target roles. Blank strings are ignored, while non-string
    values are rejected as invalid profile data.
    """
    raw_target_roles = profile_data.get("target_roles")

    if raw_target_roles is None:
        return ()

    if not isinstance(raw_target_roles, list):
        raise ValueError(
            "Career profile field 'target_roles' must be a list of strings."
        )

    target_roles: list[str] = []

    for value in raw_target_roles:
        if not isinstance(value, str):
            raise ValueError(
                "Career profile field 'target_roles' must contain only strings."
            )

        role = value.strip()

        if role:
            target_roles.append(role)

    return normalize_job_queries(tuple(target_roles))


def resolve_job_queries(config: WorkflowConfig) -> tuple[str, ...]:
    """
    Resolve the job-search queries for one workflow run.

    Explicit queries from the command line take priority. When no explicit
    queries are provided, target_roles are read from the career profile.
    """
    if config.job_queries:
        return config.job_queries

    profile_data = load_career_profile(config.profile_path)
    target_roles = extract_target_roles(profile_data)

    if target_roles:
        return target_roles

    raise ValueError(
        "No job search queries were provided and no target roles were found "
        f"in {config.profile_path}. Provide at least one --query option or "
        "add at least one value to target_roles in the career profile."
    )