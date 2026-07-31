from preference_aware_job_recommender.scoring import (
    calculate_skill_match,
    normalize_text,
)


def test_normalize_text_handles_case_and_spacing() -> None:
    assert normalize_text("  Python  ") == "python"
    assert normalize_text("Machine   Learning") == "machine learning"


def test_calculate_skill_match_identifies_matches_and_missing_skills() -> None:
    profile = {
        "skills": ["Python", "SQL", "Git", "React", "machine learning"],
    }

    job = {
        "required_skills": ["Python", "SQL", "Docker"],
        "preferred_skills": ["AWS", "Git"],
    }

    result = calculate_skill_match(profile, job)

    assert result["matched_required_skills"] == ["Python", "SQL"]
    assert result["matched_preferred_skills"] == ["Git"]
    assert result["missing_required_skills"] == ["Docker"]
    assert result["missing_preferred_skills"] == ["AWS"]
    assert result["missing_skills"] == ["Docker", "AWS"]
    assert result["skill_match_score"] == 63


def test_calculate_skill_match_returns_100_when_all_skills_match() -> None:
    profile = {
        "skills": ["Python", "SQL", "Git", "Docker", "AWS"],
    }

    job = {
        "required_skills": ["Python", "SQL", "Git"],
        "preferred_skills": ["Docker", "AWS"],
    }

    result = calculate_skill_match(profile, job)

    assert result["skill_match_score"] == 100
    assert result["missing_skills"] == []


def test_calculate_skill_match_is_case_insensitive() -> None:
    profile = {
        "skills": ["python", "sql", "git"],
    }

    job = {
        "required_skills": ["Python", "SQL", "Git"],
        "preferred_skills": [],
    }

    result = calculate_skill_match(profile, job)

    assert result["skill_match_score"] == 100
    assert result["matched_required_skills"] == ["Python", "SQL", "Git"]


def test_calculate_skill_match_returns_zero_when_job_has_no_skills() -> None:
    profile = {
        "skills": ["Python", "SQL"],
    }

    job = {
        "required_skills": [],
        "preferred_skills": [],
    }

    result = calculate_skill_match(profile, job)

    assert result["skill_match_score"] == 0
    assert result["matched_skills"] == []
    assert result["missing_skills"] == []