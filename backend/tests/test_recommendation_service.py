from __future__ import annotations

import json
from collections.abc import Mapping
from datetime import UTC, datetime
from pathlib import Path
from uuid import UUID

import pytest
from pydantic import ValidationError

from careervoice_ai_web_app.models import (
    ProfileReview,
)
from careervoice_ai_web_app.recommendation_models import (
    RecommendationDocument,
    RecommendationSettings,
)
from careervoice_ai_web_app.session_workspace import (
    SessionWorkspace,
)
from careervoice_ai_web_app.user_models import AppUser
from careervoice_ai_web_app.workflow_service import (
    ProfileConfirmationResult,
    RecommendationRunResult,
)

from backend.app.recommendation_service import (
    RecommendationService,
)


TEST_USER_ID = UUID(
    "11111111-2222-3333-4444-555555555555"
)


def career_profile() -> dict[str, object]:
    return {
        "target_roles": [
            "backend developer",
        ],
        "skills": [
            "Python",
        ],
        "experience_level": "junior",
        "preferred_locations": [
            "Adelaide",
        ],
        "preferred_work_types": [
            "hybrid",
        ],
        "liked_areas": [],
        "disliked_areas": [],
        "hard_constraints": [],
        "career_goals": [],
        "notes": [],
    }


def normalized_job() -> dict[str, object]:
    return {
        "job_id": "adzuna-1",
        "title": "Junior Backend Developer",
        "company": "Example Company",
        "location": "Adelaide",
        "work_type": "hybrid",
        "seniority": "junior",
        "description": (
            "Build Python backend services."
        ),
        "required_skills": [
            "Python",
        ],
        "preferred_skills": [],
        "responsibilities": [
            "Build backend services.",
        ],
        "tags": [
            "backend",
        ],
        "source": "adzuna",
        "source_url": (
            "https://example.com/job/1"
        ),
        "collected_at": datetime(
            2026,
            9,
            12,
            6,
            0,
            tzinfo=UTC,
        ),
    }


def recommendation_document(
    *,
    scorer: str,
) -> RecommendationDocument:
    return RecommendationDocument.from_mapping(
        {
            "recommendations": [
                {
                    "job_id": "adzuna-1",
                    "title": (
                        "Junior Backend Developer"
                    ),
                    "company": "Example Company",
                    "match_score": 88,
                    "recommendation_level": (
                        "strong_match"
                    ),
                    "reasons": [
                        "Strong Python alignment.",
                    ],
                    "missing_skills": [
                        "Docker",
                    ],
                    "penalties": [],
                    "uncertainties": [],
                    "is_rejected_by_constraints": (
                        False
                    ),
                    "scoring_method": scorer,
                    "score_breakdown": {
                        "skill_match": 35,
                    },
                    "matched_details": {
                        "matched_skills": [
                            "Python",
                        ],
                    },
                }
            ],
            "total_jobs_scored": 1,
            "total_recommendations_returned": 1,
            "scoring_method": scorer,
        }
    )


class FakeRecommendationWorkflow:
    def __init__(
        self,
        *,
        should_fail: bool = False,
    ) -> None:
        self.should_fail = should_fail

        self.confirm_calls: list[
            dict[str, object]
        ] = []

        self.rank_calls: list[
            dict[str, object]
        ] = []

        self.jobs_seen: list[
            dict[str, object]
        ] = []

    def confirm_profile(
        self,
        *,
        profile: Mapping[str, object],
        profile_edits: Mapping[str, object],
        workspace: SessionWorkspace,
    ) -> ProfileConfirmationResult:
        self.confirm_calls.append(
            {
                "profile": profile,
                "profile_edits": profile_edits,
                "workspace": workspace,
            }
        )

        review = ProfileReview.from_profile(
            profile
        ).with_edits(
            profile_edits
        )

        workspace.ensure_exists()

        workspace.profile_path.write_text(
            "{}",
            encoding="utf-8",
        )

        return ProfileConfirmationResult(
            workspace=workspace,
            review=review,
            job_queries=review.target_roles,
        )

    def rank_jobs(
        self,
        *,
        scorer: object,
        max_results: object,
        exclude_rejected: object,
        workspace: SessionWorkspace,
    ) -> RecommendationRunResult:
        self.rank_calls.append(
            {
                "scorer": scorer,
                "max_results": max_results,
                "exclude_rejected": (
                    exclude_rejected
                ),
                "workspace": workspace,
            }
        )

        self.jobs_seen = json.loads(
            workspace.jobs_output_path.read_text(
                encoding="utf-8",
            )
        )

        if self.should_fail:
            raise RuntimeError(
                "Recommendation generation failed."
            )

        settings = RecommendationSettings.from_values(
            scorer=scorer,
            max_results=max_results,
            exclude_rejected=exclude_rejected,
        )

        return RecommendationRunResult(
            workspace=workspace,
            settings=settings,
            document=recommendation_document(
                scorer=settings.scorer
            ),
        )


class FakeRecommendationWorkflowFactory:
    def __init__(
        self,
        workflow: FakeRecommendationWorkflow,
    ) -> None:
        self.workflow = workflow
        self.user_seen: AppUser | None = None
        self.output_language_seen: str | None = None

    def __call__(
        self,
        *,
        user: AppUser,
        output_language: str,
    ) -> FakeRecommendationWorkflow:
        self.user_seen = user
        self.output_language_seen = (
            output_language
        )

        return self.workflow


def create_user() -> AppUser:
    return AppUser(
        id=TEST_USER_ID,
        email="tester@example.com",
        auth_provider="supabase",
        auth_subject="provider-user-123",
        enabled=True,
    )


def test_recommendation_uses_reviewed_profile_and_jobs(
    tmp_path: Path,
) -> None:
    user = create_user()
    workflow = FakeRecommendationWorkflow()

    factory = (
        FakeRecommendationWorkflowFactory(
            workflow
        )
    )

    service = RecommendationService(
        workflow_factory=factory,
        temporary_root=tmp_path,
    )

    result = service.recommend(
        user=user,
        profile=career_profile(),
        jobs=[
            normalized_job(),
        ],
        scorer="llm",
        max_results=5,
        exclude_rejected=True,
        output_language="zh-CN",
    )

    assert factory.user_seen is user
    assert (
        factory.output_language_seen
        == "zh-CN"
    )

    assert len(workflow.confirm_calls) == 1
    assert len(workflow.rank_calls) == 1

    rank_call = workflow.rank_calls[0]

    assert rank_call["scorer"] == "llm"
    assert rank_call["max_results"] == 5
    assert (
        rank_call["exclude_rejected"]
        is True
    )

    assert len(workflow.jobs_seen) == 1

    assert (
        workflow.jobs_seen[0]["job_id"]
        == "adzuna-1"
    )

    assert (
        workflow.jobs_seen[0]["title"]
        == "Junior Backend Developer"
    )

    assert result.settings.scorer == "llm"
    assert result.settings.max_results == 5

    assert (
        result.document.recommendations[0][
            "missing_skills"
        ]
        == ["Docker"]
    )

    assert (
        result.output_language
        == "zh-CN"
    )

    workspace = rank_call["workspace"]

    assert isinstance(
        workspace,
        SessionWorkspace,
    )

    assert not workspace.directory.exists()


def test_recommendation_cleans_workspace_after_failure(
    tmp_path: Path,
) -> None:
    workflow = FakeRecommendationWorkflow(
        should_fail=True
    )

    service = RecommendationService(
        workflow_factory=(
            FakeRecommendationWorkflowFactory(
                workflow
            )
        ),
        temporary_root=tmp_path,
    )

    with pytest.raises(
        RuntimeError,
        match="Recommendation generation failed",
    ):
        service.recommend(
            user=create_user(),
            profile=career_profile(),
            jobs=[
                normalized_job(),
            ],
            scorer="rules",
            max_results=5,
            exclude_rejected=False,
            output_language="en",
        )

    assert len(workflow.rank_calls) == 1

    workspace = (
        workflow.rank_calls[0]["workspace"]
    )

    assert isinstance(
        workspace,
        SessionWorkspace,
    )

    assert not workspace.directory.exists()


def test_recommendation_rejects_invalid_job_before_ranking(
    tmp_path: Path,
) -> None:
    workflow = FakeRecommendationWorkflow()

    service = RecommendationService(
        workflow_factory=(
            FakeRecommendationWorkflowFactory(
                workflow
            )
        ),
        temporary_root=tmp_path,
    )

    invalid_job = normalized_job()
    invalid_job.pop(
        "job_id"
    )

    with pytest.raises(
        ValidationError
    ):
        service.recommend(
            user=create_user(),
            profile=career_profile(),
            jobs=[
                invalid_job,
            ],
            scorer="rules",
            max_results=5,
            exclude_rejected=False,
            output_language="en",
        )

    assert workflow.confirm_calls == []
    assert workflow.rank_calls == []