from preference_aware_job_recommender.scoring import (
    get_recommendation_level,
    score_job,
)
import pytest


def test_get_recommendation_level() -> None:
    assert get_recommendation_level(90) == "strong_match"
    assert get_recommendation_level(70) == "good_match"
    assert get_recommendation_level(45) == "partial_match"
    assert get_recommendation_level(20) == "poor_match"


def test_score_job_combines_positive_match_factors() -> None:
    profile = {
        "target_roles": ["backend developer"],
        "skills": ["Python", "SQL", "Git"],
        "experience_level": "junior",
        "preferred_locations": ["Adelaide", "remote"],
        "preferred_work_types": ["remote"],
        "liked_areas": ["backend development", "software engineering"],
        "career_goals": ["move toward software engineering"],
    }

    job = {
        "job_id": "job_001",
        "title": "Junior Backend Developer",
        "company": "Example Tech",
        "location": "Adelaide",
        "work_type": "remote",
        "seniority": "junior",
        "description": "Build backend services for software engineering teams.",
        "required_skills": ["Python", "SQL", "Git"],
        "preferred_skills": ["Docker", "AWS"],
        "responsibilities": ["Develop backend features"],
        "tags": ["backend development", "software engineering"],
    }

    result = score_job(profile, job)

    assert result["match_score"] == 90
    assert result["recommendation_level"] == "strong_match"
    assert result["missing_skills"] == ["Docker", "AWS"]
    assert result["score_breakdown"]["skill_match"] == 30
    assert result["score_breakdown"]["target_role_match"] == 20
    assert result["score_breakdown"]["experience_match"] == 10
    assert result["score_breakdown"]["location_match"] == 10
    assert result["score_breakdown"]["work_type_match"] == 10
    assert result["score_breakdown"]["liked_area_match"] == 5
    assert result["score_breakdown"]["career_goal_match"] == 5


def test_score_job_handles_location_and_work_type_mismatch() -> None:
    profile = {
        "target_roles": ["backend developer"],
        "skills": ["React", "Git"],
        "experience_level": "junior",
        "preferred_locations": ["Adelaide", "remote"],
        "preferred_work_types": ["remote"],
        "liked_areas": ["software engineering"],
        "career_goals": ["move toward software engineering"],
    }

    job = {
        "job_id": "job_006",
        "title": "Junior Frontend Developer",
        "company": "Example Web Studio",
        "location": "Melbourne",
        "work_type": "onsite",
        "seniority": "junior",
        "description": "Build user interfaces for software engineering projects.",
        "required_skills": ["React", "Git", "JavaScript"],
        "preferred_skills": ["TypeScript", "CSS"],
        "responsibilities": ["Build reusable frontend components"],
        "tags": ["frontend development", "software engineering"],
    }

    result = score_job(profile, job)

    assert result["score_breakdown"]["location_match"] == 0
    assert result["score_breakdown"]["work_type_match"] == 0
    assert result["score_breakdown"]["experience_match"] == 10
    assert result["recommendation_level"] == "partial_match"


def test_score_job_can_match_career_goal_keywords() -> None:
    profile = {
        "target_roles": ["backend developer"],
        "skills": ["Python", "Git"],
        "experience_level": "junior",
        "preferred_locations": ["remote"],
        "preferred_work_types": ["remote"],
        "liked_areas": ["AI tools"],
        "career_goals": ["move toward AI or software engineering"],
    }

    job = {
        "job_id": "job_007",
        "title": "AI Tools Intern",
        "company": "Example AI Lab",
        "location": "Remote",
        "work_type": "remote",
        "seniority": "intern",
        "description": "Assist with building simple AI-powered tools.",
        "required_skills": ["Python", "Git"],
        "preferred_skills": ["machine learning", "APIs", "SQL"],
        "responsibilities": ["Prototype small AI tools"],
        "tags": ["AI tools", "software engineering"],
    }

    result = score_job(profile, job)

    assert result["score_breakdown"]["career_goal_match"] == 5
    assert result["score_breakdown"]["liked_area_match"] == 5
    assert result["score_breakdown"]["location_match"] == 10
    assert result["score_breakdown"]["work_type_match"] == 10


def test_score_job_localizes_reasons_in_simplified_chinese() -> None:
    profile = {
        "target_roles": [
            "backend developer",
        ],
        "skills": [
            "Python",
            "SQL",
            "Git",
        ],
        "experience_level": "junior",
        "preferred_locations": [
            "Adelaide",
        ],
        "preferred_work_types": [
            "remote",
        ],
        "liked_areas": [
            "backend development",
        ],
        "disliked_areas": [],
        "hard_constraints": [],
        "career_goals": [
            "move toward software engineering",
        ],
    }

    job = {
        "job_id": "job_zh",
        "title": "Junior Backend Developer",
        "company": "Example Tech",
        "location": "Adelaide",
        "work_type": "remote",
        "seniority": "junior",
        "description": (
            "Build backend services for "
            "software engineering teams."
        ),
        "required_skills": [
            "Python",
            "SQL",
            "Git",
        ],
        "preferred_skills": [],
        "responsibilities": [
            "Develop backend features",
        ],
        "tags": [
            "backend development",
            "software engineering",
        ],
    }

    result = score_job(
        profile,
        job,
        output_language="zh-CN",
    )

    assert (
        "匹配技能：Python, SQL, Git"
        in result["reasons"]
    )

    assert (
        "匹配目标岗位：backend developer"
        in result["reasons"]
    )

    assert (
        "匹配经验水平：junior"
        in result["reasons"]
    )

    assert (
        "匹配偏好地区：Adelaide"
        in result["reasons"]
    )

    assert (
        "匹配偏好工作方式：remote"
        in result["reasons"]
    )

    assert (
        "匹配感兴趣领域：backend development"
        in result["reasons"]
    )

    assert (
        "支持职业目标：move toward software engineering"
        in result["reasons"]
    )


def test_score_job_rejects_unknown_output_language() -> None:
    with pytest.raises(
        ValueError,
        match="output_language must be one of",
    ):
        score_job(
            {},
            {},
            output_language="fr",
        )