from preference_aware_job_recommender.recommender import recommend_jobs
from preference_aware_job_recommender.scoring import score_job


def test_recommend_jobs_handles_empty_job_list() -> None:
    result = recommend_jobs(profile={}, jobs=[], scorer="rules")

    assert result["recommendations"] == []
    assert result["total_jobs_scored"] == 0
    assert result["total_recommendations_returned"] == 0
    assert result["scoring_method"] == "rules"


def test_recommend_jobs_allows_zero_max_results() -> None:
    jobs = [
        {
            "job_id": "job_001",
            "title": "Junior Python Developer",
            "company": "Example Tech",
            "required_skills": ["Python"],
            "preferred_skills": [],
        }
    ]

    result = recommend_jobs(
        profile={"skills": ["Python"]},
        jobs=jobs,
        max_results=0,
        scorer="rules"
    )

    assert result["total_jobs_scored"] == 1
    assert result["total_recommendations_returned"] == 0
    assert result["recommendations"] == []


def test_score_job_does_not_award_points_for_missing_optional_fields() -> None:
    profile = {
        "skills": ["Python"],
    }

    job = {
        "job_id": "job_001",
        "title": "Python Developer",
        "company": "Example Tech",
        "required_skills": ["Python"],
        "preferred_skills": [],
    }

    result = score_job(profile=profile, job=job)

    assert result["score_breakdown"]["skill_match"] == 40
    assert result["score_breakdown"]["experience_match"] == 0
    assert result["score_breakdown"]["location_match"] == 0
    assert result["score_breakdown"]["work_type_match"] == 0
    assert result["match_score"] == 40