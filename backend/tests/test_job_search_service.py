from __future__ import annotations

from collections.abc import Mapping, Sequence
from pathlib import Path
from uuid import UUID

import pytest

from careervoice_ai_web_app.models import (
    JobSearchSettings,
    ProfileReview,
)
from careervoice_ai_web_app.session_workspace import (
    SessionWorkspace,
)
from careervoice_ai_web_app.user_models import AppUser
from careervoice_ai_web_app.workflow_service import (
    JobSearchResult,
    ProfileConfirmationResult,
)

from backend.app.job_search_service import (
    JobSearchService,
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


class FakeJobSearchWorkflow:
    def __init__(
        self,
        *,
        should_fail: bool = False,
    ) -> None:
        self.should_fail = should_fail

        self.confirm_calls: list[
            dict[str, object]
        ] = []

        self.search_calls: list[
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

    def search_jobs(
        self,
        *,
        roles: Sequence[object],
        location: object,
        max_results_per_role: object,
        source: str,
        workspace: SessionWorkspace,
    ) -> JobSearchResult:
        self.search_calls.append(
            {
                "roles": roles,
                "location": location,
                "max_results_per_role": (
                    max_results_per_role
                ),
                "source": source,
                "workspace": workspace,
            }
        )

        if self.should_fail:
            raise RuntimeError(
                "Job search failed."
            )

        settings = JobSearchSettings.from_values(
            roles=roles,
            location=location,
            max_results_per_role=(
                max_results_per_role
            ),
            source=source,
        )

        return JobSearchResult(
            workspace=workspace,
            settings=settings,
            jobs=[
                {
                    "id": "job-1",
                    "title": "Junior Backend Developer",
                    "company": "Example Company",
                    "location": "Adelaide",
                },
                {
                    "id": "job-2",
                    "title": "Python Developer",
                    "company": "Another Company",
                    "location": "Adelaide",
                },
            ],
        )


class FakeJobSearchWorkflowFactory:
    def __init__(
        self,
        workflow: FakeJobSearchWorkflow,
    ) -> None:
        self.workflow = workflow
        self.user_seen: AppUser | None = None
        self.output_language_seen: str | None = None

    def __call__(
        self,
        *,
        user: AppUser,
        output_language: str,
    ) -> FakeJobSearchWorkflow:
        self.user_seen = user
        self.output_language_seen = (
            output_language
        )

        return self.workflow


class FakeJobSearchUsageRecorder:
    def __init__(self) -> None:
        self.users_seen: list[AppUser] = []

    def record_job_search(
        self,
        *,
        user: AppUser,
    ) -> None:
        self.users_seen.append(
            user
        )


def create_user() -> AppUser:
    return AppUser(
        id=TEST_USER_ID,
        email="tester@example.com",
        auth_provider="supabase",
        auth_subject="provider-user-123",
        enabled=True,
    )


def test_job_search_uses_reviewed_profile_and_settings(
    tmp_path: Path,
) -> None:
    usage_recorder = FakeJobSearchUsageRecorder()
    user = create_user()
    workflow = FakeJobSearchWorkflow()

    factory = FakeJobSearchWorkflowFactory(
        workflow
    )

    service = JobSearchService(
        workflow_factory=factory,
        usage_recorder=usage_recorder,
        temporary_root=tmp_path,
    )

    result = service.search(
        user=user,
        profile=career_profile(),
        roles=[
            "backend developer",
            "python developer",
        ],
        location="Adelaide",
        max_results_per_role=5,
        source="adzuna",
        output_language="zh-CN",
    )

    assert factory.user_seen is user
    assert (
        factory.output_language_seen
        == "zh-CN"
    )

    assert len(workflow.confirm_calls) == 1
    assert len(workflow.search_calls) == 1

    search_call = workflow.search_calls[0]

    assert search_call["roles"] == [
        "backend developer",
        "python developer",
    ]
    assert search_call["location"] == "Adelaide"
    assert (
        search_call["max_results_per_role"]
        == 5
    )
    assert search_call["source"] == "adzuna"

    assert result.settings.roles == (
        "backend developer",
        "python developer",
    )
    assert result.settings.location == "Adelaide"
    assert result.settings.max_results_per_role == 5
    assert result.settings.source == "adzuna"

    assert len(result.jobs) == 2
    assert (
        result.jobs[0]["title"]
        == "Junior Backend Developer"
    )

    assert result.output_language == "zh-CN"

    workspace = search_call["workspace"]

    assert isinstance(
        workspace,
        SessionWorkspace,
    )
    assert not workspace.directory.exists()
    assert usage_recorder.users_seen == [
        user
    ]


def test_job_search_cleans_workspace_after_failure(
    tmp_path: Path,
) -> None:
    usage_recorder = FakeJobSearchUsageRecorder()
    workflow = FakeJobSearchWorkflow(
        should_fail=True
    )

    service = JobSearchService(
        workflow_factory=(
            FakeJobSearchWorkflowFactory(
                workflow
            )
        ),
        usage_recorder=usage_recorder,
        temporary_root=tmp_path,
    )

    with pytest.raises(
        RuntimeError,
        match="Job search failed",
    ):
        service.search(
            user=create_user(),
            profile=career_profile(),
            roles=[
                "backend developer",
            ],
            location="Adelaide",
            max_results_per_role=5,
            source="adzuna",
            output_language="en",
        )

    assert len(workflow.search_calls) == 1

    workspace = (
        workflow.search_calls[0][
            "workspace"
        ]
    )

    assert isinstance(
        workspace,
        SessionWorkspace,
    )
    assert not workspace.directory.exists()
    assert usage_recorder.users_seen == []