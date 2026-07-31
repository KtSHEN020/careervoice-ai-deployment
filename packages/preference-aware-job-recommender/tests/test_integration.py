import json
from pathlib import Path

from preference_aware_job_recommender.data_loader import (
    load_career_profile,
    load_jobs,
)
from preference_aware_job_recommender.exporter import (
    export_recommendations_to_json,
)
from preference_aware_job_recommender.recommender import recommend_jobs


EXAMPLES_DIR = Path("examples")


def test_example_workflow_returns_ranked_recommendations() -> None:
    profile = load_career_profile(EXAMPLES_DIR / "career_profile.json")
    jobs = load_jobs(EXAMPLES_DIR / "jobs.json")

    result = recommend_jobs(profile=profile, jobs=jobs, scorer="rules")

    recommendations = result["recommendations"]
    scores = [
        recommendation["match_score"]
        for recommendation in recommendations
    ]

    assert result["total_jobs_scored"] == len(jobs)
    assert result["total_recommendations_returned"] == len(jobs)
    assert len(recommendations) > 0
    assert scores == sorted(scores, reverse=True)
    assert recommendations[0]["is_rejected_by_constraints"] is False


def test_example_workflow_can_filter_rejected_jobs() -> None:
    profile = load_career_profile(EXAMPLES_DIR / "career_profile.json")
    jobs = load_jobs(EXAMPLES_DIR / "jobs.json")

    result = recommend_jobs(
        profile=profile,
        jobs=jobs,
        include_rejected=False,
        scorer="rules"
    )

    recommendations = result["recommendations"]

    assert result["total_jobs_scored"] == len(jobs)
    assert len(recommendations) < len(jobs)
    assert all(
        recommendation["is_rejected_by_constraints"] is False
        for recommendation in recommendations
    )


def test_example_workflow_can_export_top_three_results(
    tmp_path: Path,
) -> None:
    profile = load_career_profile(EXAMPLES_DIR / "career_profile.json")
    jobs = load_jobs(EXAMPLES_DIR / "jobs.json")

    result = recommend_jobs(
        profile=profile,
        jobs=jobs,
        max_results=3,
        include_rejected=False,
        scorer="rules"
    )

    output_path = tmp_path / "recommendations.json"

    export_recommendations_to_json(
        result=result,
        output_path=output_path,
    )

    with output_path.open(encoding="utf-8") as file:
        exported_result = json.load(file)

    assert output_path.exists()
    assert exported_result == result
    assert exported_result["total_recommendations_returned"] == 3