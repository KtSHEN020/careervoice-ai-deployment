from __future__ import annotations

import pytest

from careervoice_ai_web_app.models import (
    JobSearchSettings,
    ProfileReview,
    normalize_job_search_roles,
    normalize_string_list,
    normalize_target_roles,
)


def test_normalize_target_roles_cleans_and_deduplicates_values() -> None:
    roles = normalize_target_roles(
        [
            " software developer ",
            "Backend Developer",
            "software developer",
            "",
            "  ",
        ]
    )

    assert roles == (
        "software developer",
        "Backend Developer",
    )


def test_normalize_string_list_supports_other_profile_fields() -> None:
    skills = normalize_string_list(
        [
            " Python ",
            "SQL",
            "python",
            "",
        ],
        field_name="skills",
    )

    assert skills == (
        "Python",
        "SQL",
    )


def test_profile_review_allows_profile_without_target_roles() -> None:
    review = ProfileReview.from_profile(
        {
            "skills": ["Python"],
        }
    )

    assert review.target_roles == ()
    assert review.profile == {
        "skills": ["Python"],
        "target_roles": [],
    }


def test_profile_review_rejects_invalid_list_field() -> None:
    with pytest.raises(ValueError, match="skills.*list of strings"):
        ProfileReview.from_profile(
            {
                "target_roles": ["software developer"],
                "skills": "Python",
            }
        )


def test_profile_review_applies_edits_and_preserves_extra_fields() -> None:
    review = ProfileReview.from_profile(
        {
            "target_roles": ["software developer"],
            "skills": ["Python"],
            "experience_level": None,
            "source_version": "1.0",
        }
    )

    updated_review = review.with_edits(
        {
            "target_roles": [
                " junior backend developer ",
                "Python developer",
            ],
            "skills": ["Python", "SQL", "python"],
            "experience_level": " junior ",
            "preferred_locations": [" Adelaide "],
            "preferred_work_types": ["hybrid"],
            "liked_areas": ["backend development"],
            "disliked_areas": ["sales"],
            "hard_constraints": ["not senior positions"],
            "career_goals": ["build backend experience"],
            "notes": ["Open to learning cloud tools"],
        }
    )

    assert updated_review.target_roles == (
        "junior backend developer",
        "Python developer",
    )
    assert updated_review.profile == {
        "target_roles": [
            "junior backend developer",
            "Python developer",
        ],
        "skills": ["Python", "SQL"],
        "experience_level": "junior",
        "source_version": "1.0",
        "preferred_locations": ["Adelaide"],
        "preferred_work_types": ["hybrid"],
        "liked_areas": ["backend development"],
        "disliked_areas": ["sales"],
        "hard_constraints": ["not senior positions"],
        "career_goals": ["build backend experience"],
        "notes": ["Open to learning cloud tools"],
    }


def test_confirmed_profile_requires_at_least_one_target_role() -> None:
    review = ProfileReview.from_profile(
        {
            "target_roles": ["software developer"],
        }
    )

    with pytest.raises(ValueError, match="At least one target role"):
        review.with_edits(
            {
                "target_roles": ["", "  "],
            }
        )


def test_profile_review_rejects_unsupported_edit_field() -> None:
    review = ProfileReview.from_profile(
        {
            "target_roles": ["software developer"],
        }
    )

    with pytest.raises(ValueError, match="Unsupported profile fields"):
        review.with_edits(
            {
                "unknown_field": "value",
            }
        )


def test_job_search_roles_are_cleaned_and_deduplicated() -> None:
    roles = normalize_job_search_roles(
        [
            " software developer ",
            "Backend Developer",
            "SOFTWARE DEVELOPER",
            "",
        ]
    )

    assert roles == (
        "software developer",
        "Backend Developer",
    )


def test_job_search_settings_normalize_user_input() -> None:
    settings = JobSearchSettings.from_values(
        roles=[
            " software developer ",
            "backend developer",
        ],
        location=" Adelaide ",
        max_results_per_role=5,
        source="ADZUNA",
    )

    assert settings.roles == (
        "software developer",
        "backend developer",
    )
    assert settings.location == "Adelaide"
    assert settings.max_results_per_role == 5
    assert settings.source == "adzuna"


def test_job_search_settings_reject_invalid_result_limit() -> None:
    with pytest.raises(ValueError, match="between 1 and 50"):
        JobSearchSettings.from_values(
            roles=["software developer"],
            location="Adelaide",
            max_results_per_role=0,
        )


def test_job_search_settings_calculate_maximum_raw_results() -> None:
    settings = JobSearchSettings.from_values(
        roles=[
            "software developer",
            "backend developer",
            "data analyst",
        ],
        location=None,
        max_results_per_role=5,
    )

    assert settings.maximum_raw_results == 15