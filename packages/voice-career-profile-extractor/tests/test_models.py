from voice_career_profile_extractor.models import CareerProfile


def test_career_profile_defaults():
    profile = CareerProfile()

    assert profile.target_roles == []
    assert profile.skills == []
    assert profile.experience_level is None
    assert profile.preferred_locations == []
    assert profile.preferred_work_types == []
    assert profile.liked_areas == []
    assert profile.disliked_areas == []
    assert profile.hard_constraints == []
    assert profile.career_goals == []
    assert profile.notes == []


def test_career_profile_lists_are_not_shared():
    first_profile = CareerProfile()
    second_profile = CareerProfile()

    first_profile.skills.append("Python")

    assert first_profile.skills == ["Python"]
    assert second_profile.skills == []


def test_career_profile_to_dict():
    profile = CareerProfile(
        target_roles=["junior software developer"],
        skills=["Python", "SQL", "Git"],
        experience_level="junior",
        preferred_locations=["Adelaide", "remote"],
        preferred_work_types=["remote", "hybrid"],
        liked_areas=["backend development", "data-related roles"],
        disliked_areas=["sales", "customer service"],
        hard_constraints=["avoid sales roles"],
        career_goals=["move toward AI or software engineering"],
        notes=[],
    )

    assert profile.to_dict() == {
        "target_roles": ["junior software developer"],
        "skills": ["Python", "SQL", "Git"],
        "experience_level": "junior",
        "preferred_locations": ["Adelaide", "remote"],
        "preferred_work_types": ["remote", "hybrid"],
        "liked_areas": ["backend development", "data-related roles"],
        "disliked_areas": ["sales", "customer service"],
        "hard_constraints": ["avoid sales roles"],
        "career_goals": ["move toward AI or software engineering"],
        "notes": [],
    }
