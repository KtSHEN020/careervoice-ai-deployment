import json
from pathlib import Path

from voice_career_profile_extractor.exporters import (
    profile_to_json,
    save_profile_json,
)
from voice_career_profile_extractor.models import CareerProfile


def create_sample_profile() -> CareerProfile:
    return CareerProfile(
        target_roles=["junior software developer"],
        skills=["Python", "SQL", "Git"],
        experience_level="junior",
        preferred_locations=["Adelaide", "remote"],
        preferred_work_types=["remote"],
        liked_areas=["backend development", "data-related roles"],
        disliked_areas=["sales", "customer service"],
        hard_constraints=["avoid sales roles", "avoid customer service roles"],
        career_goals=["move toward AI or software engineering"],
        notes=[],
    )


def test_profile_to_json_outputs_valid_json():
    profile = create_sample_profile()

    json_text = profile_to_json(profile)
    parsed_json = json.loads(json_text)

    assert parsed_json == profile.to_dict()
    assert '"target_roles": [' in json_text
    assert '"skills": [' in json_text


def test_save_profile_json_writes_json_file(tmp_path: Path):
    profile = create_sample_profile()
    output_path = tmp_path / "profile.json"

    saved_path = save_profile_json(profile, output_path)

    assert saved_path == output_path
    assert output_path.exists()

    parsed_json = json.loads(output_path.read_text(encoding="utf-8"))

    assert parsed_json == profile.to_dict()


def test_save_profile_json_creates_parent_directory(tmp_path: Path):
    profile = create_sample_profile()
    output_path = tmp_path / "outputs" / "profile.json"

    saved_path = save_profile_json(profile, output_path)

    assert saved_path == output_path
    assert output_path.exists()

    parsed_json = json.loads(output_path.read_text(encoding="utf-8"))

    assert parsed_json["skills"] == ["Python", "SQL", "Git"]
