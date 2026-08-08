from __future__ import annotations

import pytest

from careervoice_ai_web_app.recommendation_models import (
    RecommendationDocument,
    RecommendationSettings,
)


def make_recommendation_document() -> dict[str, object]:
    return {
        "recommendations": [
            {
                "job_id": "job-1",
                "title": "Junior Software Developer",
                "company": "Example Company",
                "match_score": 84,
                "recommendation_level": "strong_match",
                "reasons": [
                    "Matches the preferred role.",
                ],
                "missing_skills": [
                    "Docker",
                ],
                "penalties": [],
                "uncertainties": [],
                "is_rejected_by_constraints": False,
                "scoring_method": "rules",
                "score_breakdown": {
                    "skill_match": 30,
                },
                "matched_details": {
                    "matched_skills": ["Python"],
                },
            }
        ],
        "total_jobs_scored": 3,
        "total_recommendations_returned": 1,
        "scoring_method": "rules",
    }


def test_recommendation_settings_normalize_values() -> None:
    settings = RecommendationSettings.from_values(
        scorer=" LLM ",
        max_results=5,
        exclude_rejected=True,
    )

    assert settings.scorer == "llm"
    assert settings.max_results == 5
    assert settings.exclude_rejected is True


def test_recommendation_settings_reject_unsupported_scorer() -> None:
    with pytest.raises(
        ValueError,
        match="Unsupported ranking method",
    ):
        RecommendationSettings.from_values(
            scorer="unsupported",
            max_results=5,
            exclude_rejected=False,
        )


def test_recommendation_settings_reject_invalid_limit() -> None:
    with pytest.raises(
        ValueError,
        match="between 1 and 50",
    ):
        RecommendationSettings.from_values(
            scorer="rules",
            max_results=0,
            exclude_rejected=False,
        )


def test_recommendation_document_validates_output() -> None:
    document = RecommendationDocument.from_mapping(
        make_recommendation_document()
    )

    assert document.total_jobs_scored == 3
    assert document.total_recommendations_returned == 1
    assert document.scoring_method == "rules"
    assert document.recommendations[0]["match_score"] == 84


def test_recommendation_document_rejects_invalid_score() -> None:
    data = make_recommendation_document()
    recommendations = data["recommendations"]
    assert isinstance(recommendations, list)

    recommendations[0]["match_score"] = 101

    with pytest.raises(
        ValueError,
        match="between 0 and 100",
    ):
        RecommendationDocument.from_mapping(data)


def test_recommendation_document_rejects_count_mismatch() -> None:
    data = make_recommendation_document()
    data["total_recommendations_returned"] = 2

    with pytest.raises(
        ValueError,
        match="count does not match",
    ):
        RecommendationDocument.from_mapping(data)