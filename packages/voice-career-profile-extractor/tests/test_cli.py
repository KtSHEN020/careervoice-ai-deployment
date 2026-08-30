import json
from pathlib import Path

import pytest

from voice_career_profile_extractor import cli
from voice_career_profile_extractor.models import CareerProfile


def create_sample_transcript_file(tmp_path: Path) -> Path:
    transcript_file = tmp_path / "sample_input.txt"
    transcript_file.write_text(
        """
        I am looking for a junior software developer role in Adelaide or remote.
        I know Python, SQL, and Git.
        I do not want sales roles.
        """,
        encoding="utf-8",
    )

    return transcript_file


def test_cli_file_mode_defaults_to_rules_and_prints_json(
    tmp_path: Path,
    capsys,
):
    transcript_file = create_sample_transcript_file(tmp_path)

    exit_code = cli.main(["file", str(transcript_file)])

    captured = capsys.readouterr()
    parsed_json = json.loads(captured.out)

    assert exit_code == 0
    assert parsed_json["target_roles"] == ["junior software developer"]
    assert parsed_json["skills"] == ["Python", "SQL", "Git"]
    assert parsed_json["experience_level"] == "junior"
    assert parsed_json["preferred_locations"] == ["Adelaide", "remote"]
    assert parsed_json["disliked_areas"] == ["sales"]


def test_cli_file_mode_saves_json_to_output_file(
    tmp_path: Path,
    capsys,
):
    transcript_file = create_sample_transcript_file(tmp_path)
    output_file = tmp_path / "outputs" / "profile.json"

    exit_code = cli.main(
        [
            "file",
            str(transcript_file),
            "--extractor",
            "rules",
            "--output",
            str(output_file),
        ]
    )

    captured = capsys.readouterr()
    parsed_json = json.loads(output_file.read_text(encoding="utf-8"))

    assert exit_code == 0
    assert output_file.exists()
    assert "Saved career profile JSON to" in captured.out
    assert parsed_json["skills"] == ["Python", "SQL", "Git"]


def test_cli_text_mode_reads_typed_input(
    monkeypatch,
    capsys,
):
    monkeypatch.setattr(
        "builtins.input",
        lambda _: "I want a junior backend role. I know Python and SQL.",
    )

    exit_code = cli.main(["text", "--extractor", "rules"])

    captured = capsys.readouterr()
    parsed_json = json.loads(captured.out)

    assert exit_code == 0
    assert parsed_json["target_roles"] == ["backend developer"]
    assert parsed_json["skills"] == ["Python", "SQL"]
    assert parsed_json["experience_level"] == "junior"


def test_cli_uses_llm_extractor_when_selected(
    tmp_path: Path,
    monkeypatch,
    capsys,
):
    transcript_file = create_sample_transcript_file(tmp_path)
    received_values = {}

    def fake_llm_extractor(
        text: str,
        *,
        output_language: str = "en",
    ) -> CareerProfile:
        received_values["text"] = text
        received_values["output_language"] = output_language

        return CareerProfile(
            target_roles=["junior backend developer"],
            skills=["Python", "SQL"],
            experience_level="junior",
            preferred_locations=["Adelaide"],
            preferred_work_types=["hybrid"],
            liked_areas=["backend development"],
            disliked_areas=["sales"],
            hard_constraints=["avoid sales roles"],
            career_goals=["move toward software engineering"],
            notes=[],
        )

    monkeypatch.setattr(
        cli,
        "extract_career_profile_with_llm",
        fake_llm_extractor,
    )

    exit_code = cli.main(
        [
            "file",
            str(transcript_file),
            "--extractor",
            "llm",
        ]
    )

    captured = capsys.readouterr()
    parsed_json = json.loads(captured.out)

    assert exit_code == 0
    assert "junior software developer" in received_values["text"]
    assert parsed_json["target_roles"] == ["junior backend developer"]
    assert parsed_json["preferred_work_types"] == ["hybrid"]
    assert received_values["output_language"] == "en"


def test_cli_text_mode_rejects_empty_input(monkeypatch):
    monkeypatch.setattr("builtins.input", lambda _: "   ")

    with pytest.raises(
        ValueError,
        match="Typed career profile input is empty.",
    ):
        cli.main(["text"])


def test_cli_voice_mode_records_transcribes_and_uses_rules(
    monkeypatch,
    capsys,
):
    received_values = {}

    def fake_record_microphone_to_wav(output_path: str | Path) -> Path:
        path = Path(output_path)
        path.write_bytes(b"fake microphone audio")
        received_values["recording_path"] = path

        return path

    def fake_transcribe_audio_file(audio_path: str | Path) -> str:
        path = Path(audio_path)
        received_values["transcription_path"] = path
        received_values["recording_existed_during_transcription"] = path.exists()

        return "I want a junior backend role. I know Python and SQL."

    monkeypatch.setattr(
        cli,
        "record_microphone_to_wav",
        fake_record_microphone_to_wav,
    )
    monkeypatch.setattr(
        cli,
        "transcribe_audio_file",
        fake_transcribe_audio_file,
    )

    exit_code = cli.main(["voice", "--extractor", "rules"])

    captured = capsys.readouterr()
    parsed_json = json.loads(captured.out)

    recording_path = received_values["recording_path"]
    transcription_path = received_values["transcription_path"]

    assert exit_code == 0
    assert recording_path == transcription_path
    assert received_values["recording_existed_during_transcription"] is True
    assert recording_path.exists() is False
    assert "Recording career preferences from microphone." in captured.err
    assert "Transcribing recorded audio..." in captured.err
    assert parsed_json["target_roles"] == ["backend developer"]
    assert parsed_json["skills"] == ["Python", "SQL"]
    assert parsed_json["experience_level"] == "junior"


def test_cli_voice_mode_supports_llm_extractor_and_output_file(
    tmp_path: Path,
    monkeypatch,
    capsys,
):
    output_file = tmp_path / "outputs" / "profile.json"
    received_values = {}

    def fake_record_microphone_to_wav(output_path: str | Path) -> Path:
        path = Path(output_path)
        path.write_bytes(b"fake microphone audio")

        return path

    def fake_transcribe_audio_file(audio_path: str | Path) -> str:
        assert Path(audio_path).exists()

        return "I recently graduated and want to work with backend systems."

    def fake_llm_extractor(
        text: str,
        *,
        output_language: str = "en",
    ) -> CareerProfile:
        received_values["text"] = text
        received_values["output_language"] = output_language

        return CareerProfile(
            target_roles=["junior backend developer"],
            skills=["Python"],
            experience_level="junior",
            preferred_locations=[],
            preferred_work_types=[],
            liked_areas=["backend development"],
            disliked_areas=[],
            hard_constraints=[],
            career_goals=["build backend engineering experience"],
            notes=[],
        )

    monkeypatch.setattr(
        cli,
        "record_microphone_to_wav",
        fake_record_microphone_to_wav,
    )
    monkeypatch.setattr(
        cli,
        "transcribe_audio_file",
        fake_transcribe_audio_file,
    )
    monkeypatch.setattr(
        cli,
        "extract_career_profile_with_llm",
        fake_llm_extractor,
    )

    exit_code = cli.main(
        [
            "voice",
            "--extractor",
            "llm",
            "--output",
            str(output_file),
        ]
    )

    captured = capsys.readouterr()
    parsed_json = json.loads(output_file.read_text(encoding="utf-8"))

    assert exit_code == 0
    assert output_file.exists()
    assert "Saved career profile JSON to" in captured.out
    assert received_values["text"] == (
        "I recently graduated and want to work with backend systems."
    )
    assert parsed_json["target_roles"] == ["junior backend developer"]
    assert parsed_json["career_goals"] == ["build backend engineering experience"]


def test_cli_passes_simplified_chinese_to_llm_extractor(
    tmp_path: Path,
    monkeypatch,
    capsys,
):
    transcript_file = create_sample_transcript_file(
        tmp_path
    )

    received_values = {}

    def fake_llm_extractor(
        text: str,
        *,
        output_language: str = "en",
    ) -> CareerProfile:
        received_values["text"] = text
        received_values[
            "output_language"
        ] = output_language

        return CareerProfile(
            target_roles=[
                "junior software developer",
            ],
            skills=[
                "Python",
            ],
            experience_level="junior",
            preferred_locations=[
                "Adelaide",
            ],
            preferred_work_types=[
                "hybrid",
            ],
            liked_areas=[
                "后端开发",
            ],
            disliked_areas=[],
            hard_constraints=[],
            career_goals=[
                "积累软件工程经验",
            ],
            notes=[],
        )

    monkeypatch.setattr(
        cli,
        "extract_career_profile_with_llm",
        fake_llm_extractor,
    )

    exit_code = cli.main(
        [
            "file",
            str(transcript_file),
            "--extractor",
            "llm",
            "--output-language",
            "zh-CN",
        ]
    )

    capsys.readouterr()

    assert exit_code == 0

    assert (
        received_values[
            "output_language"
        ]
        == "zh-CN"
    )