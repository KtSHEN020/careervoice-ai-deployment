from __future__ import annotations

from typing import Any, Literal

from preference_aware_job_recommender.llm_scorer import (
    DEFAULT_LLM_MODEL,
    OpenAIClient,
    score_job_with_llm,
)
from preference_aware_job_recommender.scoring import score_job


ScoringMethod = Literal["rules", "llm"]
VALID_SCORERS = {"rules", "llm"}


def _validate_scorer(scorer: str) -> None:
    """
    Validate the selected scoring method.
    """
    if scorer not in VALID_SCORERS:
        raise ValueError("scorer must be one of: rules, llm.")


def _add_scoring_method(
    recommendation: dict[str, Any],
    scoring_method: ScoringMethod,
) -> dict[str, Any]:
    """
    Ensure each recommendation includes its scoring method.
    """
    if "scoring_method" in recommendation:
        return recommendation

    return {
        **recommendation,
        "scoring_method": scoring_method,
    }


def _score_job_with_selected_scorer(
    profile: dict[str, Any],
    job: dict[str, Any],
    *,
    scorer: ScoringMethod,
    llm_client: OpenAIClient | None,
    llm_model: str,
) -> dict[str, Any]:
    """
    Score one job using the selected scoring method.
    """
    if scorer == "rules":
        recommendation = score_job(profile, job)
        return _add_scoring_method(recommendation, "rules")

    recommendation = score_job_with_llm(
        profile=profile,
        job=job,
        client=llm_client,
        model=llm_model,
    )
    return _add_scoring_method(recommendation, "llm")


def recommend_jobs(
    profile: dict[str, Any],
    jobs: list[dict[str, Any]],
    max_results: int | None = None,
    include_rejected: bool = True,
    scorer: ScoringMethod = "llm",
    llm_client: OpenAIClient | None = None,
    llm_model: str = DEFAULT_LLM_MODEL,
) -> dict[str, Any]:
    """
    Return ranked job recommendations for a career profile.
    """
    _validate_scorer(scorer)

    if max_results is not None and max_results < 0:
        raise ValueError("max_results must be greater than or equal to 0.")

    recommendations = [
        _score_job_with_selected_scorer(
            profile=profile,
            job=job,
            scorer=scorer,
            llm_client=llm_client,
            llm_model=llm_model,
        )
        for job in jobs
    ]

    if not include_rejected:
        recommendations = [
            recommendation
            for recommendation in recommendations
            if not recommendation["is_rejected_by_constraints"]
        ]

    ranked_recommendations = sorted(
        recommendations,
        key=lambda recommendation: (
            recommendation["match_score"],
            not recommendation["is_rejected_by_constraints"],
        ),
        reverse=True,
    )

    if max_results is not None:
        ranked_recommendations = ranked_recommendations[:max_results]

    return {
        "recommendations": ranked_recommendations,
        "total_jobs_scored": len(jobs),
        "total_recommendations_returned": len(ranked_recommendations),
        "scoring_method": scorer,
    }