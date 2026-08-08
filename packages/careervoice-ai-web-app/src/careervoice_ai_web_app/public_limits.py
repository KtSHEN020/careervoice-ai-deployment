"""Request-size safeguards for the deployed CareerVoice AI application."""

from collections.abc import Sequence

MAX_CAREER_TEXT_CHARACTERS = 12_000
MAX_TRANSCRIPT_CHARACTERS = 12_000
MAX_ADDITIONAL_PREFERENCES_CHARACTERS = 4_000

MAX_JOB_QUERIES = 3
MAX_JOB_RESULTS_PER_QUERY = 10
MAX_RECOMMENDATIONS = 10


class PublicRequestLimitError(ValueError):
    """Raised when a public application request exceeds a safe limit."""


def validate_text_length(
    value: str,
    *,
    field_name: str,
    max_characters: int,
) -> None:
    """Reject text that exceeds an application request limit."""
    if max_characters < 1:
        raise ValueError(
            "max_characters must be a positive integer."
        )

    if len(value) > max_characters:
        raise PublicRequestLimitError(
            f"{field_name} is too long. "
            f"The maximum is {max_characters:,} characters."
        )


def validate_job_search_limits(
    queries: Sequence[str],
    *,
    max_results: int,
) -> None:
    """Validate public job-search request limits."""
    if len(queries) > MAX_JOB_QUERIES:
        raise PublicRequestLimitError(
            "Too many job-search roles were provided. "
            f"Choose at most {MAX_JOB_QUERIES} roles."
        )

    if max_results < 1:
        raise ValueError(
            "max_results must be at least 1."
        )

    if max_results > MAX_JOB_RESULTS_PER_QUERY:
        raise PublicRequestLimitError(
            "Too many listings were requested for each role. "
            f"The maximum is {MAX_JOB_RESULTS_PER_QUERY}."
        )


def validate_recommendation_limit(
    max_results: int,
) -> None:
    """Validate the maximum recommendation count."""
    if max_results < 1:
        raise ValueError(
            "max_results must be at least 1."
        )

    if max_results > MAX_RECOMMENDATIONS:
        raise PublicRequestLimitError(
            "Too many recommendations were requested. "
            f"The maximum is {MAX_RECOMMENDATIONS}."
        )