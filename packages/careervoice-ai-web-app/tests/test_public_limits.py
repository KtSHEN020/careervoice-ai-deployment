import pytest

from careervoice_ai_web_app.public_limits import (
    MAX_ADDITIONAL_PREFERENCES_CHARACTERS,
    MAX_CAREER_TEXT_CHARACTERS,
    MAX_JOB_QUERIES,
    MAX_JOB_RESULTS_PER_QUERY,
    MAX_RECOMMENDATIONS,
    MAX_TRANSCRIPT_CHARACTERS,
    PublicRequestLimitError,
    validate_job_search_limits,
    validate_recommendation_limit,
    validate_text_length,
)


def test_career_text_at_limit_is_allowed() -> None:
    validate_text_length(
        "a" * MAX_CAREER_TEXT_CHARACTERS,
        field_name="Career information",
        max_characters=MAX_CAREER_TEXT_CHARACTERS,
    )


def test_career_text_over_limit_is_rejected() -> None:
    with pytest.raises(
        PublicRequestLimitError,
        match="Career information is too long",
    ):
        validate_text_length(
            "a" * (MAX_CAREER_TEXT_CHARACTERS + 1),
            field_name="Career information",
            max_characters=MAX_CAREER_TEXT_CHARACTERS,
        )


def test_transcript_over_limit_is_rejected() -> None:
    with pytest.raises(
        PublicRequestLimitError,
        match="Transcript is too long",
    ):
        validate_text_length(
            "a" * (MAX_TRANSCRIPT_CHARACTERS + 1),
            field_name="Transcript",
            max_characters=MAX_TRANSCRIPT_CHARACTERS,
        )


def test_additional_preferences_over_limit_are_rejected() -> None:
    with pytest.raises(
        PublicRequestLimitError,
        match="Additional preferences is too long",
    ):
        validate_text_length(
            "a" * (
                MAX_ADDITIONAL_PREFERENCES_CHARACTERS + 1
            ),
            field_name="Additional preferences",
            max_characters=(
                MAX_ADDITIONAL_PREFERENCES_CHARACTERS
            ),
        )


def test_job_search_allows_public_maximum() -> None:
    validate_job_search_limits(
        tuple(
            f"role-{index}"
            for index in range(MAX_JOB_QUERIES)
        ),
        max_results=MAX_JOB_RESULTS_PER_QUERY,
    )


def test_job_search_rejects_too_many_roles() -> None:
    with pytest.raises(
        PublicRequestLimitError,
        match="Too many job-search roles",
    ):
        validate_job_search_limits(
            tuple(
                f"role-{index}"
                for index in range(MAX_JOB_QUERIES + 1)
            ),
            max_results=1,
        )


def test_job_search_rejects_too_many_results_per_role() -> None:
    with pytest.raises(
        PublicRequestLimitError,
        match="Too many listings",
    ):
        validate_job_search_limits(
            ("software developer",),
            max_results=MAX_JOB_RESULTS_PER_QUERY + 1,
        )


def test_recommendation_limit_rejects_excessive_count() -> None:
    validate_recommendation_limit(
        MAX_RECOMMENDATIONS
    )

    with pytest.raises(
        PublicRequestLimitError,
        match="Too many recommendations",
    ):
        validate_recommendation_limit(
            MAX_RECOMMENDATIONS + 1
        )