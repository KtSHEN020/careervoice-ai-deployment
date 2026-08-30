from preference_aware_job_recommender.scoring import score_job


def test_score_job_applies_disliked_area_penalty() -> None:
    profile = {
        "target_roles": ["data analyst"],
        "skills": ["Python", "SQL"],
        "experience_level": "junior",
        "preferred_locations": ["Remote"],
        "preferred_work_types": ["remote"],
        "liked_areas": ["data-related roles"],
        "disliked_areas": ["customer service"],
        "hard_constraints": [],
        "career_goals": ["move toward data-related roles"],
    }

    job = {
        "job_id": "job_005",
        "title": "Customer Support Analyst",
        "company": "Example Support Co",
        "location": "Remote",
        "work_type": "remote",
        "seniority": "junior",
        "description": "Help customers resolve support issues and analyse ticket data.",
        "required_skills": ["SQL"],
        "preferred_skills": ["Python"],
        "responsibilities": ["Respond to customer service tickets"],
        "tags": ["customer service", "support", "data-related roles"],
    }

    result = score_job(profile, job)

    assert result["score_breakdown"]["dislike_penalty"] == 15
    assert result["is_rejected_by_constraints"] is False
    assert "Contains disliked area: customer service" in result["penalties"]


def test_score_job_applies_hard_constraint_penalty() -> None:
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

    job = {
        "job_id": "job_003",
        "title": "Technical Sales Consultant",
        "company": "Example Sales Group",
        "location": "Remote",
        "work_type": "remote",
        "seniority": "junior",
        "description": "Support sales conversations for technical products.",
        "required_skills": ["Python"],
        "preferred_skills": [],
        "responsibilities": ["Join sales calls"],
        "tags": ["sales"],
    }

    result = score_job(profile, job)

    assert result["is_rejected_by_constraints"] is True
    assert result["match_score"] <= 25
    assert result["recommendation_level"] == "poor_match"
    assert result["score_breakdown"]["hard_constraint_penalty"] == 40
    assert "Contains disliked area: sales" in result["penalties"]
    assert "Conflicts with hard constraint: avoid sales roles" in result["penalties"]


def test_score_job_caps_score_when_hard_constraint_conflicts() -> None:
    profile = {
        "target_roles": ["backend developer"],
        "skills": ["Python", "SQL", "Git", "Docker", "AWS"],
        "experience_level": "senior",
        "preferred_locations": ["Remote"],
        "preferred_work_types": ["remote"],
        "liked_areas": ["backend development", "software engineering"],
        "disliked_areas": ["senior roles"],
        "hard_constraints": ["avoid senior roles"],
        "career_goals": ["move toward software engineering"],
    }

    job = {
        "job_id": "job_004",
        "title": "Senior Backend Engineer",
        "company": "Example Cloud Systems",
        "location": "Remote",
        "work_type": "remote",
        "seniority": "senior",
        "description": "Lead backend development for software engineering teams.",
        "required_skills": ["Python", "SQL", "Git"],
        "preferred_skills": ["Docker", "AWS"],
        "responsibilities": ["Design backend architecture"],
        "tags": ["backend development", "software engineering", "senior roles"],
    }

    result = score_job(profile, job)

    assert result["is_rejected_by_constraints"] is True
    assert result["match_score"] <= 25
    assert result["recommendation_level"] == "poor_match"
    assert "Conflicts with hard constraint: avoid senior roles" in result["penalties"]


def test_score_job_localizes_penalties_in_simplified_chinese() -> None:
    profile = {
        "target_roles": [
            "backend developer",
        ],
        "skills": [
            "Python",
        ],
        "experience_level": "junior",
        "preferred_locations": [
            "Remote",
        ],
        "preferred_work_types": [
            "remote",
        ],
        "liked_areas": [],
        "disliked_areas": [
            "sales",
        ],
        "hard_constraints": [
            "avoid sales roles",
        ],
        "career_goals": [],
    }

    job = {
        "job_id": "job_sales_zh",
        "title": "Technical Sales Consultant",
        "company": "Example Sales Group",
        "location": "Remote",
        "work_type": "remote",
        "seniority": "junior",
        "description": (
            "Support sales conversations."
        ),
        "required_skills": [
            "Python",
        ],
        "preferred_skills": [],
        "responsibilities": [
            "Join sales calls",
        ],
        "tags": [
            "sales",
        ],
    }

    result = score_job(
        profile,
        job,
        output_language="zh-CN",
    )

    assert (
        "包含不喜欢的领域：sales"
        in result["penalties"]
    )

    assert (
        "与不可妥协要求冲突：avoid sales roles"
        in result["penalties"]
    )

    assert (
        result[
            "is_rejected_by_constraints"
        ]
        is True
    )