from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

from streamlit.testing.v1 import AppTest

from careervoice_ai_web_app.ui_state import (
    COLLECTED_JOBS_KEY,
    JOB_QUERIES_KEY,
    PROFILE_CONFIRMED_KEY,
    PROFILE_KEY,
    PROFILE_REVISION_KEY,
)

PROJECT_ROOT = Path(__file__).resolve().parents[1]
APP_PATH = PROJECT_ROOT / "app.py"
WEB_PATH = (
    PROJECT_ROOT
    / "src"
    / "careervoice_ai_web_app"
    / "web.py"
)


def test_app_renders_profile_input_form() -> None:
    app = AppTest.from_file(
        str(APP_PATH)
    ).run()

    assert len(app.exception) == 0
    assert app.title[0].value == "CareerVoice AI"

    assert app.subheader[0].value == (
        "Tell us about your career"
    )

    assert app.text_area[0].label == (
        "Career information and preferences"
    )

    assert app.selectbox[0].label == (
        "Profile creation method"
    )

    assert app.selectbox[0].value == "rules"

    assert any(
        button.label == "Generate career profile"
        for button in app.button
    )


def test_app_renders_editable_profile_review_fields() -> None:
    app = AppTest.from_file(str(APP_PATH))
    app.session_state[PROFILE_KEY] = {
        "target_roles": ["software developer"],
        "skills": ["Python"],
        "experience_level": "junior",
        "preferred_locations": ["Adelaide"],
        "preferred_work_types": ["hybrid"],
        "liked_areas": ["backend development"],
        "disliked_areas": [],
        "hard_constraints": ["not senior positions"],
        "career_goals": [],
        "notes": [],
    }
    app.session_state[PROFILE_REVISION_KEY] = 1

    app.run()

    assert len(app.exception) == 0

    text_area_labels = {
        text_area.label
        for text_area in app.text_area
    }

    assert {
        "Target roles",
        "Skills",
        "Preferred locations",
        "Preferred work types",
        "Areas you like",
        "Areas you want to avoid",
        "Non-negotiable requirements",
        "Career goals",
        "Notes and uncertainties",
    }.issubset(text_area_labels)

    assert any(
        text_input.label == "Experience level"
        for text_input in app.text_input
    )

    assert any(
        button.label == "Save and confirm profile"
        for button in app.button
    )


def test_app_renders_job_search_form_after_profile_confirmation() -> None:
    app = AppTest.from_file(str(APP_PATH))
    app.session_state[PROFILE_KEY] = {
        "target_roles": [
            "software developer",
            "backend developer",
        ],
        "preferred_locations": ["Adelaide"],
    }
    app.session_state[PROFILE_CONFIRMED_KEY] = True
    app.session_state[JOB_QUERIES_KEY] = (
        "software developer",
        "backend developer",
    )
    app.session_state[PROFILE_REVISION_KEY] = 2

    app.run()

    assert len(app.exception) == 0

    assert any(
        text_area.label == "Roles to search for"
        for text_area in app.text_area
    )

    assert any(
        text_input.label == "Search location (optional)"
        for text_input in app.text_input
    )

    assert any(
        number_input.label == "Maximum listings per role"
        for number_input in app.number_input
    )

    assert any(
        selectbox.label == "Job listing provider"
        for selectbox in app.selectbox
    )

    assert any(
        button.label == "Search for jobs"
        for button in app.button
    )


def test_app_renders_collected_job_preview() -> None:
    app = AppTest.from_file(str(APP_PATH))
    app.session_state[PROFILE_KEY] = {
        "target_roles": ["software developer"],
        "preferred_locations": ["Adelaide"],
    }
    app.session_state[PROFILE_CONFIRMED_KEY] = True
    app.session_state[JOB_QUERIES_KEY] = (
        "software developer",
    )
    app.session_state[PROFILE_REVISION_KEY] = 2
    app.session_state[COLLECTED_JOBS_KEY] = [
        {
            "job_id": "job-1",
            "title": "Junior Software Developer",
            "company": "Example Company",
            "location": "Adelaide",
            "work_type": "hybrid",
            "seniority": "junior",
        }
    ]

    app.run(timeout=15)

    assert len(app.exception) == 0

    assert any(
        subheader.value == "Job listings found"
        for subheader in app.subheader
    )

    assert len(app.dataframe) == 1

    assert any(
        download_button.label == "Download job listings"
        for download_button in app.download_button
    )


def test_user_interface_copy_avoids_internal_repository_terms() -> None:
    web_source = WEB_PATH.read_text(encoding="utf-8")

    assert "Repo 1" not in web_source
    assert "Repo 2" not in web_source
    assert "Repo 3" not in web_source
    assert "Repo 4" not in web_source
    assert "CareerVoice AI orchestrator" not in web_source
    assert "Confirm target roles" not in web_source


def test_profile_form_uses_standard_mode_when_ai_is_unavailable() -> None:
    with patch.dict(
        "os.environ",
        {
            "OPENAI_API_KEY": "",
            "ADZUNA_APP_ID": "",
            "ADZUNA_APP_KEY": "",
        },
        clear=False,
    ):
        app = AppTest.from_file(str(APP_PATH)).run()

    assert len(app.exception) == 0

    profile_method = next(
        selectbox
        for selectbox in app.selectbox
        if selectbox.label == "Profile creation method"
    )

    assert profile_method.options == [
        "Standard extraction",
    ]


def test_profile_form_offers_ai_mode_when_ai_is_available() -> None:
    with patch.dict(
        "os.environ",
        {
            "OPENAI_API_KEY": "test-openai-key",
        },
        clear=False,
    ):
        app = AppTest.from_file(str(APP_PATH)).run()

    assert len(app.exception) == 0

    profile_method = next(
        selectbox
        for selectbox in app.selectbox
        if selectbox.label == "Profile creation method"
    )

    assert profile_method.options == [
        "Standard extraction",
        "AI-assisted extraction",
    ]


def test_job_search_is_disabled_without_provider_configuration() -> None:
    with patch.dict(
        "os.environ",
        {
            "ADZUNA_APP_ID": "",
            "ADZUNA_APP_KEY": "",
        },
        clear=False,
    ):
        app = AppTest.from_file(str(APP_PATH))

        app.session_state[PROFILE_KEY] = {
            "target_roles": ["software developer"],
            "preferred_locations": ["Adelaide"],
        }
        app.session_state[PROFILE_CONFIRMED_KEY] = True
        app.session_state[JOB_QUERIES_KEY] = (
            "software developer",
        )
        app.session_state[PROFILE_REVISION_KEY] = 2

        app.run()

    assert len(app.exception) == 0

    search_button = next(
        button
        for button in app.button
        if button.label == "Search for jobs"
    )

    assert search_button.disabled is True


def test_document_input_offers_scanned_pdf_recognition_when_ai_available() -> None:
    with patch.dict(
        "os.environ",
        {
            "OPENAI_API_KEY": "test-openai-key",
        },
        clear=False,
    ):
        app = AppTest.from_file(str(APP_PATH))

        app.run()

        input_method = next(
            radio
            for radio in app.radio
            if radio.label
            == "How would you like to provide your information?"
        )

        input_method.set_value("document")
        app.run()

    assert len(app.exception) == 0

    assert any(
        checkbox.label
        == "Allow AI recognition for scanned PDFs"
        for checkbox in app.checkbox
    )


def test_document_input_hides_scanned_pdf_recognition_without_ai() -> None:
    with patch.dict(
        "os.environ",
        {
            "OPENAI_API_KEY": "",
        },
        clear=False,
    ):
        app = AppTest.from_file(str(APP_PATH))

        app.run()

        input_method = next(
            radio
            for radio in app.radio
            if radio.label
            == "How would you like to provide your information?"
        )

        input_method.set_value("document")
        app.run()

    assert len(app.exception) == 0

    assert not any(
        checkbox.label
        == "Allow AI recognition for scanned PDFs"
        for checkbox in app.checkbox
    )


def test_app_offers_voice_input_method() -> None:
    app = AppTest.from_file(
        str(APP_PATH)
    ).run()

    assert len(app.exception) == 0

    input_method = next(
        radio
        for radio in app.radio
        if radio.label
        == "How would you like to provide your information?"
    )

    assert "Speak" in input_method.options


def test_voice_input_renders_transcription_controls_when_ai_available() -> None:
    with patch.dict(
        "os.environ",
        {
            "OPENAI_API_KEY": "test-openai-key",
        },
        clear=False,
    ):
        app = AppTest.from_file(
            str(APP_PATH)
        )

        app.run()

        input_method = next(
            radio
            for radio in app.radio
            if radio.label
            == "How would you like to provide your information?"
        )

        input_method.set_value(
            "voice"
        )
        app.run()

    assert len(app.exception) == 0

    transcribe_button = next(
        button
        for button in app.button
        if button.label
        == "Transcribe recording"
    )

    assert transcribe_button.disabled is True


def test_voice_input_reports_unavailable_ai_transcription() -> None:
    with patch.dict(
        "os.environ",
        {
            "OPENAI_API_KEY": "",
        },
        clear=False,
    ):
        app = AppTest.from_file(
            str(APP_PATH)
        )

        app.run()

        input_method = next(
            radio
            for radio in app.radio
            if radio.label
            == "How would you like to provide your information?"
        )

        input_method.set_value(
            "voice"
        )
        app.run()

    assert len(app.exception) == 0

    assert any(
        "Voice transcription is not currently available"
        in warning.value
        for warning in app.warning
    )

    transcribe_button = next(
        button
        for button in app.button
        if button.label
        == "Transcribe recording"
    )

    assert transcribe_button.disabled is True


def test_voice_input_renders_editable_transcript() -> None:
    with patch.dict(
        "os.environ",
        {
            "OPENAI_API_KEY": "test-openai-key",
        },
        clear=False,
    ):
        app = AppTest.from_file(
            str(APP_PATH)
        )

        app.session_state[
            "voice_transcript_text"
        ] = (
            "I want a junior backend developer role in Adelaide. "
            "I know Python and SQL."
        )

        app.run()

        input_method = next(
            radio
            for radio in app.radio
            if radio.label
            == "How would you like to provide your information?"
        )

        input_method.set_value(
            "voice"
        )
        app.run()

    assert len(app.exception) == 0

    transcript_editor = next(
        text_area
        for text_area in app.text_area
        if text_area.label
        == "Transcribed career information"
    )

    assert transcript_editor.value == (
        "I want a junior backend developer role in Adelaide. "
        "I know Python and SQL."
    )

    assert any(
        button.label == "Generate career profile"
        for button in app.button
    )