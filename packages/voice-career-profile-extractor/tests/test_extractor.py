from voice_career_profile_extractor.extractor import extract_career_profile

SAMPLE_TEXT = """
I am looking for a junior software developer role in Adelaide or remote.
I know Python, SQL, Git, basic React, and some machine learning.
I prefer backend or data-related roles.
I do not want sales roles, customer service roles, or senior roles.
My long-term goal is to move toward AI or software engineering.
"""


def test_extract_career_profile_from_sample_text():
    profile = extract_career_profile(SAMPLE_TEXT)

    assert profile.to_dict() == {
        "target_roles": [
            "junior software developer",
            "backend developer",
            "data analyst",
        ],
        "skills": ["Python", "SQL", "Git", "React", "machine learning"],
        "experience_level": "junior",
        "preferred_locations": ["Adelaide", "remote"],
        "preferred_work_types": ["remote"],
        "liked_areas": [
            "backend development",
            "data-related roles",
        ],
        "disliked_areas": ["sales", "customer service", "senior roles"],
        "hard_constraints": [
            "avoid sales roles",
            "avoid customer service roles",
            "avoid senior roles",
        ],
        "career_goals": ["move toward AI or software engineering"],
        "notes": [],
    }


def test_extract_career_profile_adds_notes_for_missing_information():
    profile = extract_career_profile("I want a role that helps people.")

    assert profile.target_roles == []
    assert profile.skills == []
    assert profile.experience_level is None
    assert profile.preferred_locations == []
    assert profile.notes == [
        "No clear target roles found.",
        "No clear skills found.",
        "No clear experience level found.",
        "No preferred locations found.",
    ]


def test_extract_career_profile_does_not_treat_disliked_senior_as_experience():
    profile = extract_career_profile("I know Python. I do not want senior roles.")

    assert profile.skills == ["Python"]
    assert profile.experience_level is None
    assert profile.disliked_areas == ["senior roles"]
    assert profile.hard_constraints == ["avoid senior roles"]


def test_target_role_does_not_imply_liked_area():
    profile = extract_career_profile(
        "I am looking for a backend developer role."
    )

    assert profile.target_roles == [
        "backend developer",
    ]
    assert profile.liked_areas == []


def test_explicit_preference_extracts_liked_areas():
    profile = extract_career_profile(
        "I prefer backend or data-related roles."
    )

    assert profile.liked_areas == [
        "backend development",
        "data-related roles",
    ]


def test_career_goal_does_not_imply_liked_area():
    profile = extract_career_profile(
        "My goal is to move toward AI "
        "or software engineering."
    )

    assert profile.career_goals == [
        "move toward AI or software engineering",
    ]
    assert profile.liked_areas == []


def test_interested_in_extracts_liked_area():
    profile = extract_career_profile(
        "I am interested in AI."
    )

    assert profile.liked_areas == [
        "AI tools",
    ]