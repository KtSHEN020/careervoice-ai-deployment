from typing import Any

import pytest

from preference_aware_job_recommender import recommender
from preference_aware_job_recommender.recommender import recommend_jobs


def _build_fake_recommendation(
    job: dict[str, Any],
    score: int,
    *,
    rejected: bool = False,
    scoring_method: str = "fake",
) -> dict[str, Any]:
    return {
        "job_id": job["job_id"],
        "title": job.get("title", ""),
        "company": job.get("company", ""),
        "match_score": score,
        "recommendation_level": (
            "strong_match"
            if score >= 80
            else "poor_match"
        ),
        "reasons": [],
        "missing_skills": [],
        "penalties": [],
        "is_rejected_by_constraints": rejected,
        "scoring_method": scoring_method,
    }


def test_recommend_jobs_defaults_to_llm_scorer(monkeypatch) -> None:
    calls = []

    def fake_score_job_with_llm(
        profile: dict[str, Any],
        job: dict[str, Any],
        *,
        client: Any = None,
        model: str = recommender.DEFAULT_LLM_MODEL,
    ) -> dict[str, Any]:
        calls.append(
            {
                "profile": profile,
                "job_id": job["job_id"],
                "client": client,
                "model": model,
            }
        )
        return _build_fake_recommendation(
            job,
            score=job["score"],
            scoring_method="llm",
        )

    monkeypatch.setattr(
        recommender,
        "score_job_with_llm",
        fake_score_job_with_llm,
    )

    profile = {"skills": ["Python"]}
    jobs = [
        {"job_id": "job_low", "score": 50},
        {"job_id": "job_high", "score": 90},
    ]

    fake_client = object()

    result = recommend_jobs(
        profile=profile,
        jobs=jobs,
        llm_client=fake_client,
        llm_model="fake-model",
    )

    recommendations = result["recommendations"]

    assert result["scoring_method"] == "llm"
    assert recommendations[0]["job_id"] == "job_high"
    assert recommendations[1]["job_id"] == "job_low"
    assert len(calls) == 2
    assert calls[0]["client"] is fake_client
    assert calls[0]["model"] == "fake-model"
    assert result["total_jobs_scored_with_llm"] == 2
    assert (
        result["llm_candidate_limit"]
        == recommender.MAX_LLM_JOBS_PER_RUN
    )


def test_recommend_jobs_can_use_rules_scorer(monkeypatch) -> None:
    calls = []

    def fake_score_job(
        profile: dict[str, Any],
        job: dict[str, Any],
    ) -> dict[str, Any]:
        calls.append(
            {
                "profile": profile,
                "job_id": job["job_id"],
            }
        )
        return _build_fake_recommendation(
            job,
            score=job["score"],
            scoring_method="rules",
        )

    monkeypatch.setattr(recommender, "score_job", fake_score_job)

    profile = {"skills": ["Python"]}
    jobs = [
        {"job_id": "job_001", "score": 70},
    ]

    result = recommend_jobs(
        profile=profile,
        jobs=jobs,
        scorer="rules",
    )

    assert result["scoring_method"] == "rules"
    assert result["recommendations"][0]["job_id"] == "job_001"
    assert result["recommendations"][0]["scoring_method"] == "rules"
    assert result["total_jobs_scored_with_llm"] == 0
    assert result["llm_candidate_limit"] is None
    assert calls == [
        {
            "profile": profile,
            "job_id": "job_001",
        }
    ]


def test_recommend_jobs_rejects_unknown_scorer() -> None:
    with pytest.raises(ValueError, match="scorer"):
        recommend_jobs(
            profile={},
            jobs=[],
            scorer="unknown",
        )


def test_recommend_jobs_can_filter_rejected_llm_results(
    monkeypatch,
) -> None:
    def fake_score_job_with_llm(
        profile: dict[str, Any],
        job: dict[str, Any],
        *,
        client: Any = None,
        model: str = recommender.DEFAULT_LLM_MODEL,
    ) -> dict[str, Any]:
        return _build_fake_recommendation(
            job,
            score=job["score"],
            rejected=job["rejected"],
            scoring_method="llm",
        )

    monkeypatch.setattr(
        recommender,
        "score_job_with_llm",
        fake_score_job_with_llm,
    )

    jobs = [
        {
            "job_id": "accepted_job",
            "score": 80,
            "rejected": False,
        },
        {
            "job_id": "rejected_job",
            "score": 25,
            "rejected": True,
        },
    ]

    result = recommend_jobs(
        profile={},
        jobs=jobs,
        include_rejected=False,
    )

    recommendations = result["recommendations"]

    assert result["scoring_method"] == "llm"
    assert result["total_jobs_scored"] == 2
    assert result["total_jobs_scored_with_llm"] == 2
    assert result["total_recommendations_returned"] == 1
    assert recommendations[0]["job_id"] == "accepted_job"


def test_llm_scoring_is_limited_to_top_rule_candidates(
    monkeypatch,
) -> None:
    rule_calls: list[str] = []
    llm_calls: list[str] = []

    def fake_score_job(
        profile: dict[str, Any],
        job: dict[str, Any],
    ) -> dict[str, Any]:
        rule_calls.append(job["job_id"])

        return _build_fake_recommendation(
            job,
            score=job["rule_score"],
            scoring_method="rules",
        )

    def fake_score_job_with_llm(
        profile: dict[str, Any],
        job: dict[str, Any],
        *,
        client: Any = None,
        model: str = recommender.DEFAULT_LLM_MODEL,
    ) -> dict[str, Any]:
        llm_calls.append(job["job_id"])

        return _build_fake_recommendation(
            job,
            score=job["llm_score"],
            scoring_method="llm",
        )

    monkeypatch.setattr(
        recommender,
        "score_job",
        fake_score_job,
    )
    monkeypatch.setattr(
        recommender,
        "score_job_with_llm",
        fake_score_job_with_llm,
    )

    jobs = [
        {
            "job_id": f"job_{index:02d}",
            "rule_score": index,
            "llm_score": 100 - index,
        }
        for index in range(15)
    ]

    result = recommend_jobs(
        profile={},
        jobs=jobs,
        scorer="llm",
    )

    assert len(rule_calls) == 15

    assert llm_calls == [
        "job_14",
        "job_13",
        "job_12",
        "job_11",
        "job_10",
        "job_09",
        "job_08",
        "job_07",
        "job_06",
        "job_05",
    ]

    assert (
        len(llm_calls)
        == recommender.MAX_LLM_JOBS_PER_RUN
    )
    assert result["total_jobs_scored"] == 15
    assert (
        result["total_jobs_scored_with_llm"]
        == recommender.MAX_LLM_JOBS_PER_RUN
    )
    assert (
        result["llm_candidate_limit"]
        == recommender.MAX_LLM_JOBS_PER_RUN
    )


def test_rules_scoring_does_not_use_llm_candidate_limit(
    monkeypatch,
) -> None:
    rule_calls: list[str] = []

    def fake_score_job(
        profile: dict[str, Any],
        job: dict[str, Any],
    ) -> dict[str, Any]:
        rule_calls.append(job["job_id"])

        return _build_fake_recommendation(
            job,
            score=job["score"],
            scoring_method="rules",
        )

    monkeypatch.setattr(
        recommender,
        "score_job",
        fake_score_job,
    )

    jobs = [
        {
            "job_id": f"job_{index:02d}",
            "score": index,
        }
        for index in range(15)
    ]

    result = recommend_jobs(
        profile={},
        jobs=jobs,
        scorer="rules",
    )

    assert len(rule_calls) == 15
    assert len(result["recommendations"]) == 15
    assert result["total_jobs_scored"] == 15
    assert result["total_jobs_scored_with_llm"] == 0
    assert result["llm_candidate_limit"] is None