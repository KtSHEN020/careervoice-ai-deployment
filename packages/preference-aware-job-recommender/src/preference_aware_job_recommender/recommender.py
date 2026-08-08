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

MAX_LLM_JOBS_PER_RUN = 10


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


def _ranking_key(
    recommendation: dict[str, Any],
) -> tuple[int, bool]:
    """
    Return the shared ordering key used for recommendation ranking.
    """
    return (
        recommendation["match_score"],
        not recommendation["is_rejected_by_constraints"],
    )


def _rank_recommendations(
    recommendations: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """
    Rank recommendations from strongest to weakest.
    """
    return sorted(
        recommendations,
        key=_ranking_key,
        reverse=True,
    )


def _select_llm_candidate_jobs(
    profile: dict[str, Any],
    jobs: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """
    Select a bounded set of strong candidates for LLM evaluation.

    Every job first receives the inexpensive rule-based score. Only the
    strongest candidates are then sent to the LLM scorer.
    """
    scored_candidates = [
        (
            job,
            score_job(
                profile=profile,
                job=job,
            ),
        )
        for job in jobs
    ]

    ranked_candidates = sorted(
        scored_candidates,
        key=lambda candidate: _ranking_key(candidate[1]),
        reverse=True,
    )

    return [
        job
        for job, _ in ranked_candidates[:MAX_LLM_JOBS_PER_RUN]
    ]


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

    LLM scoring is bounded by first using rule-based scoring to shortlist
    at most MAX_LLM_JOBS_PER_RUN candidates.
    """
    _validate_scorer(scorer)

    if max_results is not None and max_results < 0:
        raise ValueError("max_results must be greater than or equal to 0.")

    if scorer == "llm":
        jobs_to_score = _select_llm_candidate_jobs(
            profile=profile,
            jobs=jobs,
        )
    else:
        jobs_to_score = jobs

    recommendations = [
        _score_job_with_selected_scorer(
            profile=profile,
            job=job,
            scorer=scorer,
            llm_client=llm_client,
            llm_model=llm_model,
        )
        for job in jobs_to_score
    ]

    if not include_rejected:
        recommendations = [
            recommendation
            for recommendation in recommendations
            if not recommendation["is_rejected_by_constraints"]
        ]

    ranked_recommendations = _rank_recommendations(
        recommendations
    )

    if max_results is not None:
        ranked_recommendations = ranked_recommendations[:max_results]

    return {
        "recommendations": ranked_recommendations,
        "total_jobs_scored": len(jobs),
        "total_jobs_scored_with_llm": (
            len(jobs_to_score)
            if scorer == "llm"
            else 0
        ),
        "llm_candidate_limit": (
            MAX_LLM_JOBS_PER_RUN
            if scorer == "llm"
            else None
        ),
        "total_recommendations_returned": len(
            ranked_recommendations
        ),
        "scoring_method": scorer,
    }