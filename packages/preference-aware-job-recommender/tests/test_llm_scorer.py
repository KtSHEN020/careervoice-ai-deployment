import json
from typing import Any

import pytest

from preference_aware_job_recommender.llm_scorer import (
    DEFAULT_LLM_MODEL,
    score_job_with_llm,
)
from preference_aware_job_recommender.models import LLMJobEvaluation


class FakeResponse:
    def __init__(
        self,
        parsed_evaluation: LLMJobEvaluation | None,
    ) -> None:
        self.output_parsed = parsed_evaluation


class FakeResponsesAPI:
    def __init__(
        self,
        parsed_evaluation: LLMJobEvaluation | None,
    ) -> None:
        self.parsed_evaluation = parsed_evaluation
        self.received_arguments: dict[str, Any] = {}

    def parse(self, **kwargs: Any) -> FakeResponse:
        self.received_arguments = kwargs
        return FakeResponse(self.parsed_evaluation)


class FakeOpenAIClient:
    def __init__(
        self,
        parsed_evaluation: LLMJobEvaluation | None,
    ) -> None:
        self.responses = FakeResponsesAPI(parsed_evaluation)


def create_sample_profile() -> dict[str, Any]:
    return {
        "target_roles": ["backend developer"],
        "skills": ["Python", "SQL", "Git"],
        "experience_level": "junior",
        "preferred_locations": ["Adelaide"],
        "preferred_work_types": ["remote"],
        "liked_areas": ["backend development"],
        "disliked_areas": ["sales"],
        "hard_constraints": ["avoid sales roles"],
        "career_goals": ["move toward software engineering"],
    }


def create_sample_job() -> dict[str, Any]:
    return {
        "job_id": "job_001",
        "title": "Junior Backend Developer",
        "company": "Example Tech",
        "location": "Adelaide",
        "work_type": "remote",
        "seniority": "junior",
        "description": "Build backend services.",
        "required_skills": ["Python", "SQL", "Git"],
        "preferred_skills": ["Docker", "AWS"],
        "responsibilities": ["Develop backend features"],
        "tags": ["backend development", "software engineering"],
    }


def create_sample_evaluation() -> LLMJobEvaluation:
    return LLMJobEvaluation(
        job_id="job_001",
        match_score=88,
        role_alignment="strong",
        career_goal_alignment="strong",
        matched_skills=["Python", "SQL", "Git"],
        missing_skills=["Docker", "AWS"],
        reasons=[
            "The backend responsibilities align with the user's target role.",
            "The required skills overlap with the user's current skills.",
        ],
        penalties=[],
        hard_constraint_conflicts=[],
        uncertainties=[],
    )


def test_score_job_with_llm_returns_compatible_recommendation() -> None:
    client = FakeOpenAIClient(create_sample_evaluation())

    result = score_job_with_llm(
        profile=create_sample_profile(),
        job=create_sample_job(),
        client=client,
    )

    assert result["job_id"] == "job_001"
    assert result["title"] == "Junior Backend Developer"
    assert result["company"] == "Example Tech"
    assert result["match_score"] == 88
    assert result["recommendation_level"] == "strong_match"
    assert result["missing_skills"] == ["Docker", "AWS"]
    assert result["is_rejected_by_constraints"] is False
    assert result["scoring_method"] == "llm"


def test_score_job_with_llm_sends_expected_request() -> None:
    profile = create_sample_profile()
    job = create_sample_job()
    client = FakeOpenAIClient(create_sample_evaluation())

    score_job_with_llm(
        profile=profile,
        job=job,
        client=client,
    )

    received_arguments = client.responses.received_arguments

    assert received_arguments["model"] == DEFAULT_LLM_MODEL
    assert received_arguments["text_format"] is LLMJobEvaluation
    assert received_arguments["input"][0]["role"] == "developer"

    submitted_data = json.loads(
        received_arguments["input"][1]["content"]
    )

    assert submitted_data["career_profile"] == profile
    assert submitted_data["job"] == job


def test_score_job_with_llm_uses_custom_model() -> None:
    client = FakeOpenAIClient(create_sample_evaluation())

    score_job_with_llm(
        profile=create_sample_profile(),
        job=create_sample_job(),
        client=client,
        model="custom-model",
    )

    assert client.responses.received_arguments["model"] == "custom-model"


def test_score_job_with_llm_caps_score_for_hard_constraint_conflict() -> None:
    evaluation = create_sample_evaluation()
    evaluation.match_score = 92
    evaluation.penalties = ["Contains disliked area: sales"]
    evaluation.hard_constraint_conflicts = ["avoid sales roles"]

    client = FakeOpenAIClient(evaluation)

    result = score_job_with_llm(
        profile=create_sample_profile(),
        job=create_sample_job(),
        client=client,
    )

    assert result["match_score"] == 25
    assert result["recommendation_level"] == "poor_match"
    assert result["is_rejected_by_constraints"] is True
    assert result["score_breakdown"]["llm_semantic_score"] == 92
    assert (
        "Conflicts with hard constraint: avoid sales roles"
        in result["penalties"]
    )


def test_score_job_with_llm_rejects_missing_job_id() -> None:
    job = create_sample_job()
    job["job_id"] = ""

    client = FakeOpenAIClient(create_sample_evaluation())

    with pytest.raises(ValueError, match="non-empty job_id"):
        score_job_with_llm(
            profile=create_sample_profile(),
            job=job,
            client=client,
        )


def test_score_job_with_llm_rejects_missing_parsed_output() -> None:
    client = FakeOpenAIClient(None)

    with pytest.raises(
        RuntimeError,
        match="did not include a parsed job evaluation",
    ):
        score_job_with_llm(
            profile=create_sample_profile(),
            job=create_sample_job(),
            client=client,
        )


def test_score_job_with_llm_rejects_mismatched_job_id() -> None:
    evaluation = create_sample_evaluation()
    evaluation.job_id = "different_job"

    client = FakeOpenAIClient(evaluation)

    with pytest.raises(
        RuntimeError,
        match="job_id does not match",
    ):
        score_job_with_llm(
            profile=create_sample_profile(),
            job=create_sample_job(),
            client=client,
        )