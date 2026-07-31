import pytest

from preference_aware_job_recommender.recommender import recommend_jobs


def test_recommend_jobs_returns_ranked_recommendations() -> None:
    profile = {
        "target_roles": ["backend developer"],
        "skills": ["Python", "SQL", "Git"],
        "experience_level": "junior",
        "preferred_locations": ["Remote"],
        "preferred_work_types": ["remote"],
        "liked_areas": ["backend development", "software engineering"],
        "disliked_areas": ["sales"],
        "hard_constraints": ["avoid sales roles"],
        "career_goals": ["move toward software engineering"],
    }

    jobs = [
        {
            "job_id": "job_sales",
            "title": "Technical Sales Consultant",
            "company": "Example Sales Group",
            "location": "Remote",
            "work_type": "remote",
            "seniority": "junior",
            "description": "Support sales conversations.",
            "required_skills": ["Python"],
            "preferred_skills": [],
            "responsibilities": ["Join sales calls"],
            "tags": ["sales"],
        },
        {
            "job_id": "job_backend",
            "title": "Junior Backend Developer",
            "company": "Example Tech",
            "location": "Remote",
            "work_type": "remote",
            "seniority": "junior",
            "description": "Build backend services for software engineering teams.",
            "required_skills": ["Python", "SQL", "Git"],
            "preferred_skills": ["Docker"],
            "responsibilities": ["Develop backend features"],
            "tags": ["backend development", "software engineering"],
        },
    ]

    result = recommend_jobs(profile, jobs, scorer="rules")

    recommendations = result["recommendations"]

    assert result["total_jobs_scored"] == 2
    assert result["total_recommendations_returned"] == 2
    assert recommendations[0]["job_id"] == "job_backend"
    assert recommendations[1]["job_id"] == "job_sales"


def test_recommend_jobs_can_limit_results() -> None:
    profile = {
        "target_roles": ["backend developer"],
        "skills": ["Python", "SQL", "Git"],
        "experience_level": "junior",
        "preferred_locations": ["Remote"],
        "preferred_work_types": ["remote"],
        "liked_areas": ["software engineering"],
        "disliked_areas": [],
        "hard_constraints": [],
        "career_goals": ["move toward software engineering"],
    }

    jobs = [
        {
            "job_id": "job_001",
            "title": "Junior Backend Developer",
            "company": "Example Tech",
            "location": "Remote",
            "work_type": "remote",
            "seniority": "junior",
            "description": "Build backend services.",
            "required_skills": ["Python", "SQL", "Git"],
            "preferred_skills": [],
            "responsibilities": ["Develop backend features"],
            "tags": ["software engineering"],
        },
        {
            "job_id": "job_002",
            "title": "Junior Data Analyst",
            "company": "Example Analytics",
            "location": "Remote",
            "work_type": "remote",
            "seniority": "junior",
            "description": "Analyse data with SQL.",
            "required_skills": ["SQL"],
            "preferred_skills": ["Python"],
            "responsibilities": ["Create reports"],
            "tags": ["data-related roles"],
        },
    ]

    result = recommend_jobs(profile, jobs, max_results=1, scorer="rules")

    assert result["total_jobs_scored"] == 2
    assert result["total_recommendations_returned"] == 1
    assert len(result["recommendations"]) == 1


def test_recommend_jobs_can_exclude_rejected_jobs() -> None:
    profile = {
        "target_roles": ["backend developer"],
        "skills": ["Python", "SQL", "Git"],
        "experience_level": "junior",
        "preferred_locations": ["Remote"],
        "preferred_work_types": ["remote"],
        "liked_areas": ["software engineering"],
        "disliked_areas": ["sales"],
        "hard_constraints": ["avoid sales roles"],
        "career_goals": ["move toward software engineering"],
    }

    jobs = [
        {
            "job_id": "job_backend",
            "title": "Junior Backend Developer",
            "company": "Example Tech",
            "location": "Remote",
            "work_type": "remote",
            "seniority": "junior",
            "description": "Build backend services.",
            "required_skills": ["Python", "SQL", "Git"],
            "preferred_skills": [],
            "responsibilities": ["Develop backend features"],
            "tags": ["software engineering"],
        },
        {
            "job_id": "job_sales",
            "title": "Technical Sales Consultant",
            "company": "Example Sales Group",
            "location": "Remote",
            "work_type": "remote",
            "seniority": "junior",
            "description": "Support sales conversations.",
            "required_skills": ["Python"],
            "preferred_skills": [],
            "responsibilities": ["Join sales calls"],
            "tags": ["sales"],
        },
    ]

    result = recommend_jobs(profile, jobs, include_rejected=False, scorer="rules")

    recommendations = result["recommendations"]

    assert result["total_jobs_scored"] == 2
    assert result["total_recommendations_returned"] == 1
    assert recommendations[0]["job_id"] == "job_backend"


def test_recommend_jobs_rejects_negative_max_results() -> None:
    with pytest.raises(ValueError, match="max_results"):
        recommend_jobs(profile={}, jobs=[], max_results=-1, scorer="rules")