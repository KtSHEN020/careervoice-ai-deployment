from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass

PROFILE_LIST_FIELDS = (
    "target_roles",
    "skills",
    "preferred_locations",
    "preferred_work_types",
    "liked_areas",
    "disliked_areas",
    "hard_constraints",
    "career_goals",
    "notes",
)

EDITABLE_PROFILE_FIELDS = (
    "target_roles",
    "skills",
    "experience_level",
    "preferred_locations",
    "preferred_work_types",
    "liked_areas",
    "disliked_areas",
    "hard_constraints",
    "career_goals",
    "notes",
)

SUPPORTED_JOB_SOURCES = ("adzuna",)
MIN_RESULTS_PER_QUERY = 1
MAX_RESULTS_PER_QUERY = 50


def normalize_string_list(
    values: Sequence[object],
    *,
    field_name: str,
) -> tuple[str, ...]:
    """Clean and deduplicate a profile list while preserving order."""
    if isinstance(values, (str, bytes)):
        raise ValueError(
            f"Profile field '{field_name}' must be a list of strings."
        )

    normalized_values: list[str] = []
    seen_values: set[str] = set()

    for value in values:
        if not isinstance(value, str):
            raise ValueError(
                f"Profile field '{field_name}' must contain only strings."
            )

        cleaned_value = value.strip()

        if not cleaned_value:
            continue

        comparison_key = cleaned_value.casefold()

        if comparison_key in seen_values:
            continue

        seen_values.add(comparison_key)
        normalized_values.append(cleaned_value)

    return tuple(normalized_values)


def normalize_target_roles(values: Sequence[object]) -> tuple[str, ...]:
    """Clean and deduplicate editable target roles while preserving order."""
    return normalize_string_list(
        values,
        field_name="target_roles",
    )


def normalize_job_search_roles(
    values: Sequence[object],
) -> tuple[str, ...]:
    """Clean and deduplicate roles used for job searching."""
    if isinstance(values, (str, bytes)):
        raise ValueError(
            "Job-search roles must be provided as a list of strings."
        )

    normalized_roles: list[str] = []
    seen_roles: set[str] = set()

    for value in values:
        if not isinstance(value, str):
            raise ValueError(
                "Job-search roles must contain only strings."
            )

        role = value.strip()

        if not role:
            continue

        comparison_key = role.casefold()

        if comparison_key in seen_roles:
            continue

        seen_roles.add(comparison_key)
        normalized_roles.append(role)

    if not normalized_roles:
        raise ValueError("At least one role is required for job searching.")

    return tuple(normalized_roles)


def normalize_optional_text(
    value: object,
    *,
    field_name: str,
) -> str | None:
    """Normalize one optional text profile field."""
    if value is None:
        return None

    if not isinstance(value, str):
        raise ValueError(
            f"Profile field '{field_name}' must be text or null."
        )

    cleaned_value = value.strip()
    return cleaned_value or None


@dataclass(frozen=True)
class ProfileReview:
    """Career profile data prepared for the editable review stage."""

    profile: dict[str, object]
    target_roles: tuple[str, ...]

    @classmethod
    def from_profile(
        cls,
        profile: Mapping[str, object],
    ) -> ProfileReview:
        """Create validated review data from a structured career profile."""
        profile_copy = dict(profile)

        for field_name in PROFILE_LIST_FIELDS:
            if field_name not in profile_copy:
                continue

            raw_value = profile_copy[field_name]

            if raw_value is None:
                profile_copy[field_name] = []
                continue

            if not isinstance(raw_value, list):
                raise ValueError(
                    f"Career profile field '{field_name}' must be a "
                    "list of strings."
                )

            profile_copy[field_name] = list(
                normalize_string_list(
                    raw_value,
                    field_name=field_name,
                )
            )

        raw_target_roles = profile_copy.get("target_roles", [])

        if not isinstance(raw_target_roles, list):
            raise ValueError(
                "Career profile field 'target_roles' must be a list of strings."
            )

        target_roles = normalize_target_roles(raw_target_roles)
        profile_copy["target_roles"] = list(target_roles)

        if "experience_level" in profile_copy:
            profile_copy["experience_level"] = normalize_optional_text(
                profile_copy["experience_level"],
                field_name="experience_level",
            )

        return cls(
            profile=profile_copy,
            target_roles=target_roles,
        )

    def with_edits(
        self,
        edits: Mapping[str, object],
    ) -> ProfileReview:
        """Return validated profile data with user-reviewed field values."""
        unsupported_fields = set(edits) - set(EDITABLE_PROFILE_FIELDS)

        if unsupported_fields:
            field_list = ", ".join(sorted(unsupported_fields))
            raise ValueError(f"Unsupported profile fields: {field_list}.")

        updated_profile = dict(self.profile)

        for field_name in PROFILE_LIST_FIELDS:
            if field_name not in edits:
                continue

            raw_value = edits[field_name]

            if not isinstance(raw_value, Sequence) or isinstance(
                raw_value,
                (str, bytes),
            ):
                raise ValueError(
                    f"Profile field '{field_name}' must be a list of strings."
                )

            updated_profile[field_name] = list(
                normalize_string_list(
                    raw_value,
                    field_name=field_name,
                )
            )

        if "experience_level" in edits:
            updated_profile["experience_level"] = normalize_optional_text(
                edits["experience_level"],
                field_name="experience_level",
            )

        target_roles_value = updated_profile.get("target_roles", [])

        if not isinstance(target_roles_value, list):
            raise ValueError(
                "Career profile field 'target_roles' must be a list of strings."
            )

        normalized_target_roles = normalize_target_roles(
            target_roles_value
        )

        if not normalized_target_roles:
            raise ValueError("At least one target role is required.")

        updated_profile["target_roles"] = list(normalized_target_roles)

        return ProfileReview(
            profile=updated_profile,
            target_roles=normalized_target_roles,
        )


@dataclass(frozen=True)
class JobSearchSettings:
    """Validated settings for one web-based job search."""

    roles: tuple[str, ...]
    location: str | None
    max_results_per_role: int
    source: str = "adzuna"

    @classmethod
    def from_values(
        cls,
        *,
        roles: Sequence[object],
        location: object,
        max_results_per_role: object,
        source: str = "adzuna",
    ) -> JobSearchSettings:
        """Create validated job-search settings from user input."""
        normalized_roles = normalize_job_search_roles(roles)

        if location is None:
            normalized_location = None
        elif isinstance(location, str):
            normalized_location = location.strip() or None
        else:
            raise ValueError("Search location must be text or empty.")

        if (
            isinstance(max_results_per_role, bool)
            or not isinstance(max_results_per_role, int)
        ):
            raise ValueError(
                "Maximum listings per role must be a whole number."
            )

        if not (
            MIN_RESULTS_PER_QUERY
            <= max_results_per_role
            <= MAX_RESULTS_PER_QUERY
        ):
            raise ValueError(
                "Maximum listings per role must be between "
                f"{MIN_RESULTS_PER_QUERY} and {MAX_RESULTS_PER_QUERY}."
            )

        normalized_source = source.strip().lower()

        if normalized_source not in SUPPORTED_JOB_SOURCES:
            raise ValueError(
                f"Unsupported job listing provider: {source}."
            )

        return cls(
            roles=normalized_roles,
            location=normalized_location,
            max_results_per_role=max_results_per_role,
            source=normalized_source,
        )

    @property
    def maximum_raw_results(self) -> int:
        """Return the maximum listings requested before deduplication."""
        return len(self.roles) * self.max_results_per_role

    def to_state_dict(self) -> dict[str, object]:
        """Return settings suitable for Streamlit session state."""
        return {
            "roles": list(self.roles),
            "location": self.location,
            "max_results_per_role": self.max_results_per_role,
            "source": self.source,
        }