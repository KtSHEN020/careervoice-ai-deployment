from __future__ import annotations

from pathlib import Path
from uuid import UUID

import pytest

from careervoice_ai_web_app.models import ProfileReview
from careervoice_ai_web_app.session_workspace import (
    SessionWorkspace,
)
from careervoice_ai_web_app.user_models import AppUser
from careervoice_ai_web_app.workflow_service import (
    ProfileExtractionResult,
)

from backend.app.profile_service import (
    ProfileExtractionService,
)


TEST_USER_ID = UUID(
    "11111111-2222-3333-4444-555555555555"
)


class FakeProfileWorkflow:
    def __init__(
        self,
        *,
        should_fail: bool = False,
    ) -> None:
        self.should_fail = should_fail

        self.calls: list[
            tuple[
                str,
                str,
                SessionWorkspace,
            ]
        ] = []

    def extract_text_profile(
        self,
        *,
        career_preference_text: str,
        extractor: str,
        workspace: SessionWorkspace,
    ) -> ProfileExtractionResult:
        self.calls.append(
            (
                career_preference_text,
                extractor,
                workspace,
            )
        )

        if self.should_fail:
            raise ValueError(
                "Profile extraction failed."
            )

        return ProfileExtractionResult(
            workspace=workspace,
            review=ProfileReview.from_profile(
                {
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
                    "liked_areas": [
                        "backend development",
                    ],
                    "disliked_areas": [],
                    "hard_constraints": [],
                    "career_goals": [],
                    "notes": [],
                }
            ),
            extractor=extractor.strip().lower(),
        )


class FakeProfileWorkflowFactory:
    def __init__(
        self,
        workflow: FakeProfileWorkflow,
    ) -> None:
        self.workflow = workflow
        self.user_seen: AppUser | None = None
        self.output_language_seen: str | None = None

    def __call__(
        self,
        *,
        user: AppUser,
        output_language: str,
    ) -> FakeProfileWorkflow:
        self.user_seen = user
        self.output_language_seen = output_language

        return self.workflow


def create_user() -> AppUser:
    return AppUser(
        id=TEST_USER_ID,
        email="tester@example.com",
        auth_provider="supabase",
        auth_subject="provider-user-123",
        enabled=True,
    )


def test_text_profile_extraction_uses_user_workflow(
    tmp_path: Path,
) -> None:
    user = create_user()
    workflow = FakeProfileWorkflow()
    factory = FakeProfileWorkflowFactory(
        workflow
    )

    service = ProfileExtractionService(
        workflow_factory=factory,
        temporary_root=tmp_path,
    )

    result = service.extract_text(
        user=user,
        career_preference_text=(
            "I want a junior backend role."
        ),
        extractor="llm",
        output_language="zh-CN",
    )

    assert factory.user_seen is user
    assert factory.output_language_seen == "zh-CN"

    assert len(workflow.calls) == 1

    career_text, extractor, workspace = (
        workflow.calls[0]
    )

    assert career_text == (
        "I want a junior backend role."
    )
    assert extractor == "llm"

    assert result.profile["target_roles"] == [
        "backend developer"
    ]
    assert result.profile["skills"] == [
        "Python"
    ]
    assert result.extractor == "llm"
    assert result.output_language == "zh-CN"

    assert not workspace.directory.exists()


def test_text_profile_extraction_cleans_workspace_after_failure(
    tmp_path: Path,
) -> None:
    user = create_user()
    workflow = FakeProfileWorkflow(
        should_fail=True
    )

    service = ProfileExtractionService(
        workflow_factory=(
            FakeProfileWorkflowFactory(
                workflow
            )
        ),
        temporary_root=tmp_path,
    )

    with pytest.raises(
        ValueError,
        match="Profile extraction failed",
    ):
        service.extract_text(
            user=user,
            career_preference_text=(
                "I want a software role."
            ),
            extractor="rules",
            output_language="en",
        )

    assert len(workflow.calls) == 1

    _, _, workspace = workflow.calls[0]

    assert not workspace.directory.exists()