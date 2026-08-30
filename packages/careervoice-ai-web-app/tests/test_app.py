from __future__ import annotations

import time
from pathlib import Path
from unittest.mock import patch
from uuid import UUID

import pytest
from streamlit.testing.v1 import AppTest

from careervoice_ai_web_app.ai_usage import (
    AIUsageStatus,
)
from careervoice_ai_web_app.authentication import (
    AuthenticationSession,
)
from careervoice_ai_web_app.i18n import (
    LANGUAGE_STATE_KEY,
)
from careervoice_ai_web_app.persistent_ai_usage import (
    PersistentAIUsageBudget,
)
from careervoice_ai_web_app.public_limits import (
    MAX_ADDITIONAL_PREFERENCES_CHARACTERS,
    MAX_CAREER_TEXT_CHARACTERS,
    MAX_JOB_QUERIES,
    MAX_JOB_RESULTS_PER_QUERY,
    MAX_TRANSCRIPT_CHARACTERS,
)
from careervoice_ai_web_app.ui_state import (
    AUTHENTICATED_APP_USER_KEY,
    AUTHENTICATION_SESSION_KEY,
    COLLECTED_JOBS_KEY,
    JOB_QUERIES_KEY,
    LOGIN_CODE_REQUESTED_KEY,
    LOGIN_CODE_SENT_AT_KEY,
    LOGIN_PENDING_EMAIL_KEY,
    PROFILE_CONFIRMED_KEY,
    PROFILE_KEY,
    PROFILE_REVISION_KEY,
)
from careervoice_ai_web_app.user_models import (
    AppUser,
    AuthenticatedIdentity,
)

PROJECT_ROOT = Path(__file__).resolve().parents[1]
APP_PATH = PROJECT_ROOT / "app.py"
WEB_PATH = (
    PROJECT_ROOT
    / "src"
    / "careervoice_ai_web_app"
    / "web.py"
)

@pytest.fixture(autouse=True)
def _configure_auth_runtime(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Provide non-secret test configuration for the login runtime."""
    monkeypatch.setenv(
        "SUPABASE_URL",
        "https://example.supabase.co",
    )
    monkeypatch.setenv(
        "SUPABASE_PUBLISHABLE_KEY",
        "test-publishable-key",
    )
    monkeypatch.setenv(
        "DATABASE_HOST",
        "example.pooler.supabase.com",
    )
    monkeypatch.setenv(
        "DATABASE_PORT",
        "5432",
    )
    monkeypatch.setenv(
        "DATABASE_NAME",
        "postgres",
    )
    monkeypatch.setenv(
        "DATABASE_USER",
        "postgres.example",
    )
    monkeypatch.setenv(
        "DATABASE_PASSWORD",
        "test-password",
    )
    monkeypatch.setenv(
        "DATABASE_SSLMODE",
        "require",
    )
    monkeypatch.setattr(
        PersistentAIUsageBudget,
        "status",
        lambda self: AIUsageStatus(
            limit=40,
            used=7,
            remaining=33,
            profile_extractions=2,
            voice_transcriptions=1,
            document_recognitions=0,
            ai_ranking_runs=0,
        ),
    )


def _authenticated_app() -> AppTest:
    """Create an AppTest with an authorized CareerVoice user session."""
    identity = AuthenticatedIdentity(
        provider="supabase",
        subject="auth-user-123",
        email="tester@example.com",
    )

    authentication_session = AuthenticationSession(
        identity=identity,
        access_token="test-access-token",
        refresh_token="test-refresh-token",
        expires_at=1_800_000_000,
    )

    app_user = AppUser(
        id=UUID(
            "12345678-1234-5678-1234-567812345678"
        ),
        email="tester@example.com",
        auth_provider="supabase",
        auth_subject="auth-user-123",
        enabled=True,
    )

    app = AppTest.from_file(
        str(APP_PATH)
    )

    app.session_state[
        AUTHENTICATION_SESSION_KEY
    ] = authentication_session

    app.session_state[
        AUTHENTICATED_APP_USER_KEY
    ] = app_user

    return app


def test_unauthenticated_user_sees_login_page() -> None:
    app = AppTest.from_file(
        str(APP_PATH)
    ).run()

    assert len(app.exception) == 0

    assert app.title[0].value == (
        "CareerVoice AI"
    )

    assert any(
        subheader.value == "Sign in to continue"
        for subheader in app.subheader
    )

    assert any(
        text_input.label == "Email"
        for text_input in app.text_input
    )

    assert any(
        button.label == "Send login code"
        for button in app.button
    )

    assert not any(
        subheader.value == "Tell us about your career"
        for subheader in app.subheader
    )


def test_login_code_page_uses_persisted_pending_email() -> None:
    app = AppTest.from_file(
        str(APP_PATH)
    )

    app.session_state[
        LOGIN_CODE_REQUESTED_KEY
    ] = True

    app.session_state[
        LOGIN_PENDING_EMAIL_KEY
    ] = "tester@example.com"

    app.session_state[
        LOGIN_CODE_SENT_AT_KEY
    ] = time.time()

    app.run()

    assert len(app.exception) == 0

    assert any(
        text_input.label == "Login code"
        for text_input in app.text_input
    )

    assert any(
        button.label == "Sign in"
        for button in app.button
    )

    assert not any(
        text_input.label == "Email"
        for text_input in app.text_input
    )

    assert any(
        button.label == "Resend code"
        for button in app.button
    )

    assert any(
        button.label == "Use a different email"
        for button in app.button
    )


def test_app_renders_profile_input_form() -> None:
    app = _authenticated_app().run()

    assert len(app.exception) == 0
    assert app.title[0].value == "CareerVoice AI"

    assert app.subheader[0].value == (
        "Tell us about your career"
    )

    assert app.text_area[0].label == (
        "Career information and preferences"
    )

    assert (
        app.text_area[0].max_chars
        == MAX_CAREER_TEXT_CHARACTERS
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
    app = _authenticated_app()
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
    app = _authenticated_app()
    app.session_state[PROFILE_KEY] = {
        "target_roles": [
            "software developer",
            "backend developer",
            "data analyst",
            "QA engineer",
        ],
        "preferred_locations": ["Adelaide"],
    }
    app.session_state[PROFILE_CONFIRMED_KEY] = True
    app.session_state[JOB_QUERIES_KEY] = (
        "software developer",
        "backend developer",
        "data analyst",
        "QA engineer",
    )
    app.session_state[PROFILE_REVISION_KEY] = 2

    app.run()

    roles_input = next(
        text_area
        for text_area in app.text_area
        if text_area.label == "Roles to search for"
    )

    assert len(
        roles_input.value.splitlines()
    ) == MAX_JOB_QUERIES

    assert str(MAX_JOB_QUERIES) in roles_input.help

    max_results_input = next(
        number_input
        for number_input in app.number_input
        if number_input.label
        == "Maximum listings per role"
    )

    assert (
        max_results_input.max
        == MAX_JOB_RESULTS_PER_QUERY
    )

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
    app = _authenticated_app()
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
        app = _authenticated_app().run()

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
        app = _authenticated_app().run()

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
        app = _authenticated_app()

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
        app = _authenticated_app()

        app.run()

        input_method = next(
            radio
            for radio in app.radio
            if radio.label
            == "How would you like to provide your information?"
        )

        input_method.set_value("document")
        app.run()

        additional_preferences_input = next(
            text_area
            for text_area in app.text_area
            if text_area.label
            == "Additional career preferences (optional)"
        )

        assert (
            additional_preferences_input.max_chars
            == MAX_ADDITIONAL_PREFERENCES_CHARACTERS
        )

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
        app = _authenticated_app()

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
    app = _authenticated_app().run()

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
        app = _authenticated_app()

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
        app = _authenticated_app()

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
        app = _authenticated_app()

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

    assert (
        transcript_editor.max_chars
        == MAX_TRANSCRIPT_CHARACTERS
    )

    assert any(
        button.label == "Generate career profile"
        for button in app.button
    )


def test_authenticated_user_sees_ai_usage_status() -> None:
    app = _authenticated_app().run()

    assert len(app.exception) == 0

    assert any(
        subheader.value == "AI assistance today"
        for subheader in app.sidebar.subheader
    )

    captions = [
        caption.value
        for caption in app.sidebar.caption
    ]

    assert "33 AI units remaining" in captions
    assert "Resets daily at 00:00 UTC." in captions

    assert any(
        markdown.value == "**7 / 40 AI units used**"
        for markdown in app.sidebar.markdown
    )

    sidebar_text = " ".join(
        element.value
        for element in app.sidebar.markdown
        if isinstance(
            element.value,
            str,
        )
    )

    assert "Today's usage" in sidebar_text

    assert "AI profile creation" in sidebar_text
    assert "2 runs × 1 unit" in sidebar_text

    assert "Voice transcription" in sidebar_text
    assert "1 run × 1 unit" in sidebar_text

    assert "Document recognition" in sidebar_text
    assert "0 runs × 1 unit" in sidebar_text

    assert "AI job ranking" in sidebar_text
    assert "0 runs × 10 units" in sidebar_text


def test_login_page_renders_simplified_chinese() -> None:
    app = AppTest.from_file(
        str(APP_PATH)
    )

    app.session_state[
        LANGUAGE_STATE_KEY
    ] = "zh-CN"

    app.run()

    assert len(app.exception) == 0

    assert any(
        subheader.value == "登录以继续"
        for subheader in app.subheader
    )

    assert any(
        text_input.label == "邮箱"
        for text_input in app.text_input
    )

    assert any(
        button.label == "发送登录验证码"
        for button in app.button
    )


def test_authenticated_sidebar_renders_simplified_chinese() -> None:
    app = _authenticated_app()

    app.session_state[
        LANGUAGE_STATE_KEY
    ] = "zh-CN"

    app.run()

    assert len(app.exception) == 0

    assert any(
        button.label == "退出登录"
        for button in app.sidebar.button
    )

    assert any(
        subheader.value == "今日 AI 辅助额度"
        for subheader in app.sidebar.subheader
    )

    captions = [
        caption.value
        for caption in app.sidebar.caption
    ]

    assert "剩余 33 个 AI 单位" in captions
    assert "每日 00:00 UTC 重置。" in captions


def test_profile_input_renders_simplified_chinese() -> None:
    app = _authenticated_app()

    app.session_state[
        LANGUAGE_STATE_KEY
    ] = "zh-CN"

    app.run()

    assert len(app.exception) == 0

    assert any(
        subheader.value == "介绍你的职业情况"
        for subheader in app.subheader
    )

    assert any(
        text_area.label == "职业信息与偏好"
        for text_area in app.text_area
    )

    assert any(
        button.label == "生成职业画像"
        for button in app.button
    )


def test_profile_review_renders_simplified_chinese() -> None:
    app = _authenticated_app()

    app.session_state[
        LANGUAGE_STATE_KEY
    ] = "zh-CN"

    app.session_state[
        PROFILE_KEY
    ] = {
        "target_roles": [
            "Software Developer",
        ],
        "skills": [
            "Python",
        ],
        "experience_level": "junior",
        "preferred_locations": [
            "Adelaide",
        ],
        "preferred_work_types": [
            "hybrid",
        ],
        "liked_areas": [],
        "disliked_areas": [],
        "hard_constraints": [],
        "career_goals": [],
        "notes": [],
    }

    app.run()

    assert len(app.exception) == 0

    assert any(
        subheader.value == "检查并编辑职业画像"
        for subheader in app.subheader
    )

    labels = [
        text_area.label
        for text_area in app.text_area
    ]

    assert "目标岗位" in labels
    assert "技能" in labels
    assert "偏好地区" in labels
    assert "不可妥协的要求" in labels

    assert any(
        button.label == "保存并确认职业画像"
        for button in app.button
    )


def test_job_search_renders_simplified_chinese() -> None:
    app = _authenticated_app()

    app.session_state[
        LANGUAGE_STATE_KEY
    ] = "zh-CN"

    app.session_state[
        PROFILE_KEY
    ] = {
        "target_roles": [
            "Software Developer",
        ],
        "preferred_locations": [
            "Adelaide",
        ],
    }

    app.session_state[
        PROFILE_CONFIRMED_KEY
    ] = True

    app.session_state[
        JOB_QUERIES_KEY
    ] = (
        "Software Developer",
    )

    app.run()

    assert len(app.exception) == 0

    assert any(
        subheader.value == "配置职位搜索"
        for subheader in app.subheader
    )

    assert any(
        text_area.label == "要搜索的岗位"
        for text_area in app.text_area
    )

    assert any(
        text_input.label == "搜索地区（可选）"
        for text_input in app.text_input
    )

    assert any(
        number_input.label == "每个岗位最多职位数"
        for number_input in app.number_input
    )

    assert any(
        button.label == "搜索职位"
        for button in app.button
    )


def test_authenticated_main_copy_renders_simplified_chinese() -> None:
    app = _authenticated_app()

    app.session_state[
        LANGUAGE_STATE_KEY
    ] = "zh-CN"

    app.run()

    assert len(app.exception) == 0

    markdown_values = [
        element.value
        for element in app.markdown
        if isinstance(
            element.value,
            str,
        )
    ]

    assert (
        "将你的职业偏好转化为结构化、可解释的职位推荐。"
        in markdown_values
    )