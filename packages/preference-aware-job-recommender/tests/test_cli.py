import json
from pathlib import Path
from typing import Any

from preference_aware_job_recommender import cli
from preference_aware_job_recommender.cli import (
    build_parser,
    format_recommendations,
    main,
)


def test_build_parser_defaults_to_llm_scorer() -> None:
    parser = build_parser()
    args = parser.parse_args([])

    assert args.scorer == "llm"


def test_format_recommendations_includes_key_fields() -> None:
    result = {
        "scoring_method": "rules",
        "total_jobs_scored": 1,
        "total_recommendations_returned": 1,
        "recommendations": [
            {
                "job_id": "job_001",
                "title": "Junior Backend Developer",
                "company": "Example Tech",
                "match_score": 86,
                "recommendation_level": "strong_match",
                "reasons": [
                    "Matches skills: Python, SQL, Git",
                    "Matches experience level: junior",
                ],
                "missing_skills": ["Docker", "AWS"],
                "penalties": [],
                "is_rejected_by_constraints": False,
                "scoring_method": "rules",
            }
        ],
    }

    output = format_recommendations(result)

    assert "Preference-Aware Job Recommendations" in output
    assert "Scoring method: rules" in output
    assert "Total jobs scored: 1" in output
    assert "Junior Backend Developer" in output
    assert "Example Tech" in output
    assert "Score: 86 (strong_match)" in output
    assert "Missing skills: Docker, AWS" in output


def test_format_recommendations_handles_empty_results() -> None:
    result = {
        "scoring_method": "rules",
        "total_jobs_scored": 0,
        "total_recommendations_returned": 0,
        "recommendations": [],
    }

    output = format_recommendations(result)

    assert "No recommendations found." in output


def test_format_recommendations_includes_uncertainties() -> None:
    result = {
        "scoring_method": "llm",
        "total_jobs_scored": 1,
        "total_recommendations_returned": 1,
        "recommendations": [
            {
                "job_id": "job_001",
                "title": "Junior Backend Developer",
                "company": "Example Tech",
                "match_score": 82,
                "recommendation_level": "strong_match",
                "reasons": [],
                "missing_skills": [],
                "penalties": [],
                "uncertainties": [
                    "The listing does not clearly state whether AWS is required."
                ],
                "is_rejected_by_constraints": False,
                "scoring_method": "llm",
            }
        ],
    }

    output = format_recommendations(result)

    assert "Uncertainties:" in output
    assert "AWS is required" in output


def test_cli_main_runs_with_example_files(capsys) -> None:
    exit_code = main(
        [
            "--profile",
            "examples/career_profile.json",
            "--jobs",
            "examples/jobs.json",
            "--max-results",
            "3",
            "--scorer",
            "rules",
        ]
    )

    captured = capsys.readouterr()

    assert exit_code == 0
    assert "Preference-Aware Job Recommendations" in captured.out
    assert "Scoring method: rules" in captured.out
    assert "Total jobs scored:" in captured.out
    assert "Recommendations returned: 3" in captured.out


def test_cli_main_can_export_json(tmp_path: Path, capsys) -> None:
    output_path = tmp_path / "recommendations.json"

    exit_code = main(
        [
            "--profile",
            "examples/career_profile.json",
            "--jobs",
            "examples/jobs.json",
            "--max-results",
            "2",
            "--output",
            str(output_path),
            "--scorer",
            "rules",
        ]
    )

    captured = capsys.readouterr()

    assert exit_code == 0
    assert output_path.exists()
    assert "JSON output written to:" in captured.out

    with output_path.open(encoding="utf-8") as file:
        exported_result = json.load(file)

    assert exported_result["scoring_method"] == "rules"
    assert exported_result["total_jobs_scored"] > 0
    assert exported_result["total_recommendations_returned"] == 2
    assert len(exported_result["recommendations"]) == 2


def test_cli_main_passes_llm_options_to_recommender(monkeypatch, capsys) -> None:
    received_arguments: dict[str, Any] = {}

    def fake_recommend_jobs(**kwargs: Any) -> dict[str, Any]:
        received_arguments.update(kwargs)
        return {
            "scoring_method": kwargs["scorer"],
            "total_jobs_scored": 1,
            "total_recommendations_returned": 1,
            "recommendations": [
                {
                    "job_id": "job_001",
                    "title": "Junior Backend Developer",
                    "company": "Example Tech",
                    "match_score": 88,
                    "recommendation_level": "strong_match",
                    "reasons": [],
                    "missing_skills": [],
                    "penalties": [],
                    "uncertainties": [],
                    "is_rejected_by_constraints": False,
                    "scoring_method": kwargs["scorer"],
                }
            ],
        }

    monkeypatch.setattr(cli, "recommend_jobs", fake_recommend_jobs)

    exit_code = main(
        [
            "--profile",
            "examples/career_profile.json",
            "--jobs",
            "examples/jobs.json",
            "--scorer",
            "llm",
            "--llm-model",
            "fake-model",
        ]
    )

    captured = capsys.readouterr()

    assert exit_code == 0
    assert received_arguments["scorer"] == "llm"
    assert received_arguments["llm_model"] == "fake-model"
    assert "Scoring method: llm" in captured.out