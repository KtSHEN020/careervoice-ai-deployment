from pathlib import Path

import pytest

from careervoice_ai_orchestrator.models import WorkflowConfig


def test_workflow_config_uses_default_values() -> None:
    config = WorkflowConfig()

    assert config.input_mode == "profile"
    assert config.profile_input_path == Path("outputs/profile_input.txt")
    assert config.profile_path == Path("examples/career_profile.json")
    assert config.jobs_output_path == Path("outputs/jobs.json")
    assert config.recommendations_output_path == Path("outputs/recommendations.json")

    assert config.profile_extractor == "rules"

    assert config.job_source == "adzuna"
    assert config.job_queries == ()
    assert config.job_location == "Adelaide"
    assert config.job_max_results == 10

    assert config.recommender_scorer == "rules"
    assert config.recommendation_max_results == 10
    assert config.exclude_rejected is False
    assert config.output_language == "en"


def test_workflow_config_converts_string_paths_to_path_objects() -> None:
    config = WorkflowConfig(
        profile_input_path="custom/profile_input.txt",
        profile_path="custom/profile.json",
        jobs_output_path="custom/jobs.json",
        recommendations_output_path="custom/recommendations.json",
    )

    assert config.profile_input_path == Path("custom/profile_input.txt")
    assert config.profile_path == Path("custom/profile.json")
    assert config.jobs_output_path == Path("custom/jobs.json")
    assert config.recommendations_output_path == Path("custom/recommendations.json")


def test_workflow_config_returns_output_directories() -> None:
    config = WorkflowConfig(
        profile_input_path="outputs/input/profile_input.txt",
        profile_path="outputs/profile/career_profile.json",
        jobs_output_path="outputs/jobs/jobs.json",
        recommendations_output_path="outputs/final/recommendations.json",
    )

    assert config.output_directories == (
        Path("outputs/input"),
        Path("outputs/profile"),
        Path("outputs/jobs"),
        Path("outputs/final"),
    )


def test_workflow_config_rejects_unsupported_input_mode() -> None:
    with pytest.raises(ValueError, match="Unsupported input mode"):
        WorkflowConfig(input_mode="audio")


def test_workflow_config_rejects_unsupported_profile_extractor() -> None:
    with pytest.raises(ValueError, match="Unsupported profile extractor"):
        WorkflowConfig(profile_extractor="custom")


def test_workflow_config_rejects_unsupported_job_source() -> None:
    with pytest.raises(ValueError, match="Unsupported job source"):
        WorkflowConfig(job_source="linkedin")


def test_workflow_config_rejects_empty_job_query() -> None:
    with pytest.raises(ValueError, match="job_queries cannot contain empty values"):
        WorkflowConfig(job_queries=("   ",))


def test_workflow_config_rejects_invalid_job_max_results() -> None:
    with pytest.raises(ValueError, match="job_max_results must be at least 1"):
        WorkflowConfig(job_max_results=0)


def test_workflow_config_rejects_unsupported_recommender_scorer() -> None:
    with pytest.raises(ValueError, match="Unsupported recommender scorer"):
        WorkflowConfig(recommender_scorer="random")


def test_workflow_config_rejects_invalid_recommendation_max_results() -> None:
    with pytest.raises(ValueError, match="recommendation_max_results"):
        WorkflowConfig(recommendation_max_results=0)


def test_workflow_config_accepts_simplified_chinese() -> None:
    config = WorkflowConfig(
        output_language="zh-CN"
    )

    assert (
        config.output_language
        == "zh-CN"
    )


def test_workflow_config_rejects_unsupported_output_language() -> None:
    with pytest.raises(
        ValueError,
        match="Unsupported output language",
    ):
        WorkflowConfig(
            output_language="fr"
        )