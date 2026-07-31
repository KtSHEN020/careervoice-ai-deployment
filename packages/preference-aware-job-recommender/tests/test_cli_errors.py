from pathlib import Path

from preference_aware_job_recommender.cli import main

from preference_aware_job_recommender import config


def test_cli_reports_missing_profile_file(capsys) -> None:
    exit_code = main(
        [
            "--profile",
            "missing-profile.json",
            "--jobs",
            "examples/jobs.json",
        ]
    )

    captured = capsys.readouterr()

    assert exit_code == 1
    assert "Error: file not found: missing-profile.json" in captured.err


def test_cli_reports_invalid_profile_json(tmp_path: Path, capsys) -> None:
    profile_path = tmp_path / "career_profile.json"
    profile_path.write_text('{"skills": ["Python",}', encoding="utf-8")

    exit_code = main(
        [
            "--profile",
            str(profile_path),
            "--jobs",
            "examples/jobs.json",
        ]
    )

    captured = capsys.readouterr()

    assert exit_code == 1
    assert "Error: Invalid JSON in" in captured.err


def test_cli_reports_invalid_profile_structure(tmp_path: Path, capsys) -> None:
    profile_path = tmp_path / "career_profile.json"
    profile_path.write_text('["Python", "SQL"]', encoding="utf-8")

    exit_code = main(
        [
            "--profile",
            str(profile_path),
            "--jobs",
            "examples/jobs.json",
        ]
    )

    captured = capsys.readouterr()

    assert exit_code == 1
    assert "Career profile JSON must contain an object." in captured.err


def test_cli_reports_negative_max_results(capsys) -> None:
    exit_code = main(["--max-results", "-1", "--scorer", "rules"])

    captured = capsys.readouterr()

    assert exit_code == 1
    assert "max_results must be greater than or equal to 0." in captured.err


def test_cli_reports_missing_openai_api_key(monkeypatch, capsys) -> None:
    monkeypatch.setattr(config, "load_dotenv", lambda: None)
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)

    exit_code = main(
        [
            "--profile",
            "examples/career_profile.json",
            "--jobs",
            "examples/jobs.json",
            "--max-results",
            "1",
            "--scorer",
            "llm",
        ]
    )

    captured = capsys.readouterr()

    assert exit_code == 1
    assert "OPENAI_API_KEY is not set" in captured.err