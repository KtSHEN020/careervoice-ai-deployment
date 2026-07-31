import pytest
from pydantic import ValidationError

from preference_aware_job_recommender.models import LLMJobEvaluation


def build_valid_evaluation_data() -> dict:
    return {
        "job_id": "job_001",
        "match_score": 88,
        "role_alignment": "strong",
        "career_goal_alignment": "strong",
        "matched_skills": ["Python", "SQL", "Git"],
        "missing_skills": ["Docker", "AWS"],
        "reasons": [
            "The backend responsibilities align with the user's target role.",
            "The role matches several of the user's current technical skills.",
        ],
        "penalties": [],
        "hard_constraint_conflicts": [],
        "uncertainties": [
            "The listing does not state whether AWS experience is mandatory."
        ],
    }


def test_llm_job_evaluation_accepts_valid_data() -> None:
    evaluation = LLMJobEvaluation(**build_valid_evaluation_data())

    assert evaluation.job_id == "job_001"
    assert evaluation.match_score == 88
    assert evaluation.role_alignment == "strong"
    assert evaluation.missing_skills == ["Docker", "AWS"]


def test_llm_job_evaluation_rejects_score_above_100() -> None:
    data = build_valid_evaluation_data()
    data["match_score"] = 101

    with pytest.raises(ValidationError):
        LLMJobEvaluation(**data)


def test_llm_job_evaluation_rejects_negative_score() -> None:
    data = build_valid_evaluation_data()
    data["match_score"] = -1

    with pytest.raises(ValidationError):
        LLMJobEvaluation(**data)


def test_llm_job_evaluation_rejects_unknown_alignment_level() -> None:
    data = build_valid_evaluation_data()
    data["role_alignment"] = "fairly good"

    with pytest.raises(ValidationError):
        LLMJobEvaluation(**data)


def test_llm_job_evaluation_rejects_extra_fields() -> None:
    data = build_valid_evaluation_data()
    data["random_extra_field"] = "unexpected"

    with pytest.raises(ValidationError):
        LLMJobEvaluation(**data)
