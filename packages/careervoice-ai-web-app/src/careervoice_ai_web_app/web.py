from __future__ import annotations

import json
import logging
import time
from collections.abc import Mapping, Sequence

import streamlit as st

from careervoice_ai_web_app.ai_usage import (
    AI_RANKING_AI_UNITS,
    DOCUMENT_RECOGNITION_AI_UNITS,
    PROFILE_EXTRACTION_AI_UNITS,
    VOICE_TRANSCRIPTION_AI_UNITS,
    SupportsAIUsageBudget,
)
from careervoice_ai_web_app.auth_runtime import build_login_controller
from careervoice_ai_web_app.authentication import AuthenticationError
from careervoice_ai_web_app.errors import OrchestrationError
from careervoice_ai_web_app.login_controller import LoginController
from careervoice_ai_web_app.login_resend import (
    remaining_resend_seconds,
)
from careervoice_ai_web_app.orchestrator_gateway import (
    Repo4OrchestratorGateway,
)
from careervoice_ai_web_app.public_limits import (
    MAX_ADDITIONAL_PREFERENCES_CHARACTERS,
    MAX_CAREER_TEXT_CHARACTERS,
    MAX_JOB_QUERIES,
    MAX_JOB_RESULTS_PER_QUERY,
    MAX_TRANSCRIPT_CHARACTERS,
)
from careervoice_ai_web_app.recommendation_ui import (
    render_recommendation_workflow,
)
from careervoice_ai_web_app.runtime_check import (
    missing_runtime_dependencies,
)
from careervoice_ai_web_app.runtime_config import (
    CapabilityStatus,
    get_capability_status,
)
from careervoice_ai_web_app.session_workspace import SessionWorkspace
from careervoice_ai_web_app.ui_state import (
    COLLECTED_JOBS_KEY,
    JOB_QUERIES_KEY,
    JOB_SEARCH_SETTINGS_KEY,
    LOGIN_CODE_KEY,
    LOGIN_CODE_REQUESTED_KEY,
    LOGIN_CODE_SENT_AT_KEY,
    LOGIN_EMAIL_KEY,
    LOGIN_PENDING_EMAIL_KEY,
    PROFILE_CONFIRMED_KEY,
    PROFILE_KEY,
    WORKSPACE_SESSION_ID_KEY,
    clear_login_form_state,
    job_search_widget_key,
    profile_widget_key,
    record_job_search,
    record_profile_confirmation,
    record_profile_extraction,
)
from careervoice_ai_web_app.usage_budget_factory import (
    build_ai_usage_budget,
)
from careervoice_ai_web_app.user_access import UserAccessError
from careervoice_ai_web_app.voice_transcription import (
    Repo1VoiceTranscriber,
)
from careervoice_ai_web_app.workflow_service import (
    CareerVoiceWorkflowService,
)

LOGGER = logging.getLogger(__name__)

RUNTIME_FEATURE_NAMES = {
    "career-profile-extract": "Career profile creation",
    "job-collect": "Job searching",
    "job-recommend": "Job recommendation generation",
}

VOICE_TRANSCRIPT_KEY = "voice_transcript_text"


def _render_login(
    controller: LoginController,
) -> None:
    """Render the approved-user email login flow."""
    st.title("CareerVoice AI")
    st.subheader("Sign in to continue")

    st.write(
        "Access is limited to approved users."
    )

    code_requested = (
        st.session_state.get(
            LOGIN_CODE_REQUESTED_KEY
        )
        is True
    )

    if not code_requested:
        with st.form(
            "login_email_form"
        ):
            email = st.text_input(
                "Email",
                key=LOGIN_EMAIL_KEY,
            )

            submitted = st.form_submit_button(
                "Send login code",
                use_container_width=True,
            )

        if not submitted:
            return

        cleaned_email = email.strip()

        if not cleaned_email:
            st.error(
                "Enter your email address."
            )
            return

        try:
            controller.request_login_code(
                cleaned_email
            )
        except ValueError:
            st.error(
                "Enter a valid email address."
            )
            return
        except AuthenticationError:
            # Keep approved and unapproved email behaviour
            # indistinguishable in the user interface.
            pass
        except Exception:
            LOGGER.exception(
                "Unexpected login-code request failure."
            )

        st.session_state[
            LOGIN_PENDING_EMAIL_KEY
        ] = cleaned_email

        st.session_state[
            LOGIN_CODE_REQUESTED_KEY
        ] = True

        st.session_state[
            LOGIN_CODE_SENT_AT_KEY
        ] = time.time()

        st.rerun()
        return

    email_value = st.session_state.get(
        LOGIN_PENDING_EMAIL_KEY
    )

    if (
        not isinstance(email_value, str)
        or not email_value.strip()
    ):
        clear_login_form_state(
            st.session_state
        )
        st.rerun()
        return

    email = email_value.strip()

    st.info(
        "If this email has access, a login code has been sent. "
        "Check your inbox and spam folder."
    )

    with st.form(
        "login_code_form"
    ):
        code = st.text_input(
            "Login code",
            type="password",
            key=LOGIN_CODE_KEY,
        )

        submitted = st.form_submit_button(
            "Sign in",
            use_container_width=True,
        )

    if submitted:
        cleaned_code = code.strip()

        if not cleaned_code:
            st.error(
                "Enter the login code from your email."
            )
        else:
            try:
                controller.verify_login_code(
                    email=email,
                    code=cleaned_code,
                )
            except (
                AuthenticationError,
                UserAccessError,
            ):
                st.error(
                    "We couldn't sign you in. "
                    "Check the code and try again, "
                    "or contact the person who gave you access."
                )
            except Exception:
                LOGGER.exception(
                    "Unexpected sign-in failure."
                )

                st.error(
                    "Sign-in is temporarily unavailable. "
                    "Please try again later."
                )
            else:
                st.rerun()
                return

    sent_at = st.session_state.get(
        LOGIN_CODE_SENT_AT_KEY
    )

    remaining_seconds = remaining_resend_seconds(
        sent_at,
        now=time.time(),
    )

    question_col, resend_col, _ = st.columns(
        [1.5, 1.1, 7.1],
        vertical_alignment="center",
    )

    with question_col:
        st.write(
            "Didn't receive a code?"
        )

    with resend_col:
        resend_clicked = st.button(
            "Resend code",
            use_container_width=False,
        )

    if remaining_seconds > 0:
        st.caption(
            "You can request another code in "
            f"{remaining_seconds} seconds."
        )

    if resend_clicked:
        now = time.time()

        remaining_seconds = remaining_resend_seconds(
            st.session_state.get(
                LOGIN_CODE_SENT_AT_KEY
            ),
            now=now,
        )

        if remaining_seconds > 0:
            st.warning(
                "Please wait "
                f"{remaining_seconds} seconds "
                "before requesting another code."
            )
        else:
            try:
                controller.request_login_code(
                    email
                )
            except ValueError:
                st.error(
                    "We couldn't request another login code. "
                    "Please try using a different email."
                )
            except AuthenticationError:
                # Keep approved and unapproved email behaviour
                # indistinguishable.
                pass
            except Exception:
                LOGGER.exception(
                    "Unexpected login-code resend failure."
                )

            st.session_state[
                LOGIN_CODE_SENT_AT_KEY
            ] = now

            st.success(
                "If this email has access, "
                "a new login code has been sent."
            )

    st.button(
        "Use a different email",
        on_click=clear_login_form_state,
        args=(
            st.session_state,
        ),
    )


def _render_account_controls(
    controller: LoginController,
) -> None:
    """Render controls for the current signed-in user."""
    user = controller.current_user

    if user is None:
        return

    st.sidebar.caption(
        f"Signed in as {user.email}"
    )

    if st.sidebar.button(
        "Sign out",
        use_container_width=True,
    ):
        try:
            controller.sign_out()
        except Exception:
            # LoginController clears local state even when
            # provider sign-out fails.
            LOGGER.exception(
                "Provider sign-out failed."
            )

        st.rerun()


def _run_label(count: int) -> str:
    """Return the correct singular or plural usage label."""
    return "run" if count == 1 else "runs"


def _render_ai_usage_status(
    budget: SupportsAIUsageBudget,
) -> None:
    """Show the current user's daily AI allowance and feature usage."""
    st.sidebar.divider()

    st.sidebar.subheader(
        "AI assistance today"
    )

    try:
        status = budget.status()
    except Exception:
        LOGGER.exception(
            "Unable to load AI usage status."
        )

        st.sidebar.caption(
            "AI usage information is temporarily unavailable."
        )
        return

    if status.limit > 0:
        progress = min(
            1.0,
            max(
                0.0,
                status.used / status.limit,
            ),
        )
    else:
        progress = 0.0

    st.sidebar.write(
        f"**{status.used} / {status.limit} AI units used**"
    )

    st.sidebar.progress(
        progress
    )

    st.sidebar.caption(
        f"{status.remaining} AI units remaining"
    )

    st.sidebar.markdown(
        "**Today's usage**"
    )

    st.sidebar.write(
        "AI profile creation  \n"
        f"{status.profile_extractions} "
        f"{_run_label(status.profile_extractions)} "
        f"× {PROFILE_EXTRACTION_AI_UNITS} unit"
    )

    st.sidebar.write(
        "Voice transcription  \n"
        f"{status.voice_transcriptions} "
        f"{_run_label(status.voice_transcriptions)} "
        f"× {VOICE_TRANSCRIPTION_AI_UNITS} unit"
    )

    st.sidebar.write(
        "Document recognition  \n"
        f"{status.document_recognitions} "
        f"{_run_label(status.document_recognitions)} "
        f"× {DOCUMENT_RECOGNITION_AI_UNITS} unit"
    )

    st.sidebar.write(
        "AI job ranking  \n"
        f"{status.ai_ranking_runs} "
        f"{_run_label(status.ai_ranking_runs)} "
        f"× {AI_RANKING_AI_UNITS} units"
    )

    st.sidebar.caption(
        "All AI features share the same "
        f"{status.limit}-unit daily allowance."
    )

    st.sidebar.caption(
        "Resets daily at 00:00 UTC."
    )


def _profile_extractor_options(
    capabilities: CapabilityStatus,
) -> tuple[str, ...]:
    """Return profile extraction methods available to the user."""
    if capabilities.ai_features_available:
        return ("rules", "llm")

    return ("rules",)


def _get_or_create_workspace() -> SessionWorkspace:
    """Return the isolated workspace for this Streamlit session."""
    existing_session_id = st.session_state.get(
        WORKSPACE_SESSION_ID_KEY
    )

    if isinstance(existing_session_id, str):
        return SessionWorkspace.from_session_id(
            existing_session_id
        )

    workspace = SessionWorkspace.create()
    st.session_state[WORKSPACE_SESSION_ID_KEY] = workspace.session_id
    return workspace


def _render_runtime_status() -> frozenset[str]:
    """Show unavailable application features."""
    missing_dependencies = missing_runtime_dependencies()

    missing_commands = frozenset(
        dependency.command
        for dependency in missing_dependencies
    )

    if not missing_dependencies:
        return missing_commands

    st.warning(
        "Some features are unavailable because the application setup "
        "is incomplete."
    )

    with st.expander("Setup details"):
        for dependency in missing_dependencies:
            feature_name = RUNTIME_FEATURE_NAMES.get(
                dependency.command,
                dependency.purpose.capitalize(),
            )

            st.write(
                f"{feature_name} is currently unavailable."
            )

    return missing_commands


def _render_error(error: Exception) -> None:
    """Display a safe browser error without an uncontrolled traceback."""
    if isinstance(error, OrchestrationError):
        st.error(error.user_message)

        if error.stage == "job collection":
            st.caption(
                "Check the search settings, internet connection, and "
                "job-provider credentials configured for this application."
            )

        if error.stage == "recommendation generation":
            st.caption(
                "Try standard ranking, check the internet connection, "
                "or verify that AI access is configured for this "
                "application."
            )

        if error.technical_details:
            with st.expander("Technical details"):
                st.code(error.technical_details)

        return

    if isinstance(error, ValueError):
        st.error(str(error))
        return

    LOGGER.exception(
        "Unexpected CareerVoice AI web application error",
        exc_info=error,
    )

    st.error(
        "An unexpected application error occurred. "
        "Check the terminal logs for more information."
    )

    with st.expander("Technical details"):
        st.code(
            f"{type(error).__name__}: {error}"
        )


def _profile_list_text(
    profile: Mapping[str, object],
    field_name: str,
) -> str:
    """Convert a list profile field into one-item-per-line text."""
    value = profile.get(field_name)

    if not isinstance(value, list):
        return ""

    return "\n".join(
        item
        for item in value
        if isinstance(item, str)
    )


def _profile_text_value(
    profile: Mapping[str, object],
    field_name: str,
) -> str:
    """Return one editable text profile value."""
    value = profile.get(field_name)

    return (
        value
        if isinstance(value, str)
        else ""
    )


def _render_voice_profile_input(
    *,
    service: CareerVoiceWorkflowService,
    extraction_available: bool,
    capabilities: CapabilityStatus,
) -> None:
    """Render browser voice recording and transcript review controls."""
    st.write(
        "Record yourself describing your career background, skills, "
        "preferences, and what you are looking for next."
    )

    if not capabilities.ai_features_available:
        st.warning(
            "Voice transcription is not currently available because "
            "AI access is not configured for this application."
        )

    recorded_audio = st.audio_input(
        "Record your career information",
        sample_rate=16000,
        disabled=not capabilities.ai_features_available,
        help=(
            "Your recording is sent to the configured speech-to-text "
            "service so it can be converted into editable text."
        ),
    )

    st.caption(
        "You will be able to review and edit the transcript before "
        "CareerVoice AI creates your career profile."
    )

    transcribe_clicked = st.button(
        "Transcribe recording",
        disabled=(
            recorded_audio is None
            or not capabilities.ai_features_available
        ),
        width="stretch",
    )

    if transcribe_clicked:
        try:
            with st.spinner(
                "Transcribing your recording..."
            ):
                filename = (
                    getattr(
                        recorded_audio,
                        "name",
                        None,
                    )
                    or "career-voice.wav"
                )

                media_type = (
                    getattr(
                        recorded_audio,
                        "type",
                        None,
                    )
                    or "audio/wav"
                )

                transcript = service.transcribe_voice(
                    filename=filename,
                    content=recorded_audio.getvalue(),
                    media_type=media_type,
                )

                st.session_state[
                    VOICE_TRANSCRIPT_KEY
                ] = transcript.text

            st.success(
                "Recording transcribed. Review the text below before "
                "generating your career profile."
            )

        except Exception as error:
            _render_error(error)

    transcript_value = st.session_state.get(
        VOICE_TRANSCRIPT_KEY
    )

    if (
        not isinstance(
            transcript_value,
            str,
        )
        or not transcript_value.strip()
    ):
        return

    st.markdown(
        "#### Review your transcript"
    )

    st.write(
        "Correct anything the transcription misunderstood. "
        "The edited text, not the original recording, will be used "
        "to create your career profile."
    )

    with st.form(
        "voice_profile_form"
    ):
        edited_transcript = st.text_area(
            "Transcribed career information",
            height=220,
            max_chars=MAX_TRANSCRIPT_CHARACTERS,
            key=VOICE_TRANSCRIPT_KEY,
            help=(
                "Review names, technologies, locations, job titles, "
                "and other details before continuing. "
                f"Maximum {MAX_TRANSCRIPT_CHARACTERS:,} characters."
            ),
        )

        extractor = st.selectbox(
            "Profile creation method",
            options=_profile_extractor_options(
                capabilities
            ),
            format_func=lambda value: {
                "rules": "Standard extraction",
                "llm": "AI-assisted extraction",
            }[value],
            key="voice_profile_extractor",
        )

        if capabilities.ai_features_available:
            st.caption(
                "Voice transcription already uses the configured "
                "speech-to-text service. Standard profile extraction "
                "does not make a second AI request; AI-assisted "
                "extraction does."
            )
        else:
            st.caption(
                "Standard extraction is available. AI-assisted "
                "extraction is not currently available."
            )

        submitted = st.form_submit_button(
            "Generate career profile",
            type="primary",
            disabled=not extraction_available,
            width="stretch",
        )

    if not submitted:
        return

    workspace = _get_or_create_workspace()

    try:
        with st.status(
            "Generating your career profile...",
            expanded=True,
        ) as status:
            st.write(
                "Analyzing your reviewed transcript and preparing "
                "the details for review."
            )

            result = service.extract_text_profile(
                career_preference_text=edited_transcript,
                extractor=extractor,
                workspace=workspace,
            )

            record_profile_extraction(
                st.session_state,
                profile=result.review.profile,
                extractor=result.extractor,
            )

            status.update(
                label="Career profile generated.",
                state="complete",
                expanded=False,
            )

        st.success(
            "Your career profile is ready. Review and correct the "
            "details before continuing."
        )

    except Exception as error:
        _render_error(error)


def _render_profile_input(
    *,
    service: CareerVoiceWorkflowService,
    extraction_available: bool,
    capabilities: CapabilityStatus,
) -> None:
    """Render career information input and profile creation controls."""
    st.subheader("Tell us about your career")

    st.write(
        "You can write about your career, upload an existing CV or "
        "career document, or describe your career by speaking."
    )

    input_method = st.radio(
        "How would you like to provide your information?",
        options=(
            "write",
            "document",
            "voice",
        ),
        format_func=lambda value: {
            "write": "Write or paste",
            "document": "Upload a document",
            "voice": "Speak",
        }[value],
        horizontal=True,
    )

    if input_method == "voice":
        _render_voice_profile_input(
            service=service,
            extraction_available=extraction_available,
            capabilities=capabilities,
        )
        return

    with st.form("career_preference_form"):
        career_preference_text = ""
        uploaded_document = None
        additional_preferences = ""
        allow_image_recognition = False

        if input_method == "write":
            career_preference_text = st.text_area(
                "Career information and preferences",
                height=220,
                max_chars=MAX_CAREER_TEXT_CHARACTERS,
                placeholder=(
                    "Example: I am looking for a junior software developer "
                    "or backend developer role in Adelaide. I prefer hybrid "
                    "work and have experience with Python and SQL..."
                ),
            )

            st.caption(
                "You can describe your experience, skills, preferred roles, "
                "locations, work arrangements, constraints, and career goals. "
                f"Maximum {MAX_CAREER_TEXT_CHARACTERS:,} characters."
            )

        else:
            uploaded_document = st.file_uploader(
                "Upload your CV or career document",
                type=(
                    "txt",
                    "pdf",
                    "docx",
                ),
                help=(
                    "Supported formats: TXT, PDF, and DOCX. "
                    "Maximum file size: 5 MB."
                ),
            )

            if capabilities.ai_features_available:
                allow_image_recognition = st.checkbox(
                    "Allow AI recognition for scanned PDFs",
                    value=False,
                    help=(
                        "If the uploaded PDF contains scanned images rather than "
                        "selectable text, its pages may be sent to the configured "
                        "AI service so the document text can be recognized."
                    ),
                )

                st.caption(
                    "Normal text-based PDFs are read locally. AI recognition is "
                    "used only when a PDF has no readable text layer and you "
                    "enable the option above."
                )
            else:
                st.caption(
                    "Text-based PDFs are supported. Scanned or image-only PDFs "
                    "require AI document recognition, which is not currently "
                    "available for this application."
                )

            additional_preferences = st.text_area(
                "Additional career preferences (optional)",
                height=160,
                max_chars=MAX_ADDITIONAL_PREFERENCES_CHARACTERS,
                placeholder=(
                    "Example: I am looking for junior backend roles in "
                    "Adelaide. I prefer hybrid work and do not want "
                    "senior positions."
                ),
            )

            st.caption(
                "A CV often describes your experience but not what you want "
                "next. Add any preferred roles, locations, work arrangements, "
                "constraints, or career goals that may be missing. "
                f"Maximum {MAX_ADDITIONAL_PREFERENCES_CHARACTERS:,} characters."
            )

        extractor = st.selectbox(
            "Profile creation method",
            options=_profile_extractor_options(
                capabilities
            ),
            format_func=lambda value: {
                "rules": "Standard extraction",
                "llm": "AI-assisted extraction",
            }[value],
        )

        if capabilities.ai_features_available:
            st.caption(
                "Standard extraction is predictable and does not use an "
                "external AI service. AI-assisted extraction can understand "
                "more flexible descriptions."
            )
        else:
            st.caption(
                "Standard extraction is available. AI-assisted extraction "
                "is not currently available for this application."
            )

        submitted = st.form_submit_button(
            "Generate career profile",
            type="primary",
            disabled=not extraction_available,
            width="stretch",
        )

    if not submitted:
        return

    workspace = _get_or_create_workspace()

    try:
        with st.status(
            "Generating your career profile...",
            expanded=True,
        ) as status:
            if input_method == "write":
                st.write(
                    "Analyzing your career information and preparing the "
                    "details for review."
                )

                result = service.extract_text_profile(
                    career_preference_text=career_preference_text,
                    extractor=extractor,
                    workspace=workspace,
                )

            else:
                if uploaded_document is None:
                    raise ValueError(
                        "Upload a TXT, PDF, or DOCX document before "
                        "generating your career profile."
                    )

                st.write(
                    "Reading your document and combining it with any "
                    "additional career preferences."
                )

                result = service.extract_document_profile(
                    filename=uploaded_document.name,
                    content=uploaded_document.getvalue(),
                    additional_preferences=additional_preferences,
                    extractor=extractor,
                    workspace=workspace,
                    allow_image_recognition=allow_image_recognition,
                )

            record_profile_extraction(
                st.session_state,
                profile=result.review.profile,
                extractor=result.extractor,
            )

            status.update(
                label="Career profile generated.",
                state="complete",
                expanded=False,
            )

        st.success(
            "Your career profile is ready. Review and correct the details "
            "before continuing."
        )

    except Exception as error:
        _render_error(error)


def _render_profile_review(
    *,
    service: CareerVoiceWorkflowService,
) -> None:
    """Render an editable career profile review form."""
    profile_value = st.session_state.get(
        PROFILE_KEY
    )

    if not isinstance(profile_value, dict):
        return

    st.divider()
    st.subheader(
        "Review and edit your career profile"
    )

    st.write(
        "Check the extracted details and correct anything that is missing "
        "or inaccurate. These details will be used to search and rank jobs."
    )

    with st.form("profile_review_form"):
        st.markdown(
            "#### Roles, skills, and experience"
        )

        left_column, right_column = st.columns(
            2,
            gap="medium",
        )

        with left_column:
            target_roles_text = st.text_area(
                "Target roles",
                value=_profile_list_text(
                    profile_value,
                    "target_roles",
                ),
                height="content",
                help="Enter one role per line.",
                key=profile_widget_key(
                    st.session_state,
                    "target_roles",
                ),
            )

            skills_text = st.text_area(
                "Skills",
                value=_profile_list_text(
                    profile_value,
                    "skills",
                ),
                height="content",
                help="Enter one skill per line.",
                key=profile_widget_key(
                    st.session_state,
                    "skills",
                ),
            )

        with right_column:
            experience_level = st.text_input(
                "Experience level",
                value=_profile_text_value(
                    profile_value,
                    "experience_level",
                ),
                placeholder="Example: junior",
                key=profile_widget_key(
                    st.session_state,
                    "experience_level",
                ),
            )

            preferred_locations_text = st.text_area(
                "Preferred locations",
                value=_profile_list_text(
                    profile_value,
                    "preferred_locations",
                ),
                height="content",
                help="Enter one location per line.",
                key=profile_widget_key(
                    st.session_state,
                    "preferred_locations",
                ),
            )

        st.markdown(
            "#### Work preferences and constraints"
        )

        left_column, right_column = st.columns(
            2
        )

        with left_column:
            preferred_work_types_text = st.text_area(
                "Preferred work types",
                value=_profile_list_text(
                    profile_value,
                    "preferred_work_types",
                ),
                height="content",
                placeholder="Example: hybrid",
                help="Enter one work type per line.",
                key=profile_widget_key(
                    st.session_state,
                    "preferred_work_types",
                ),
            )

            liked_areas_text = st.text_area(
                "Areas you like",
                value=_profile_list_text(
                    profile_value,
                    "liked_areas",
                ),
                height="content",
                help="Enter one area per line.",
                key=profile_widget_key(
                    st.session_state,
                    "liked_areas",
                ),
            )

        with right_column:
            disliked_areas_text = st.text_area(
                "Areas you want to avoid",
                value=_profile_list_text(
                    profile_value,
                    "disliked_areas",
                ),
                height="content",
                help="Enter one area per line.",
                key=profile_widget_key(
                    st.session_state,
                    "disliked_areas",
                ),
            )

            hard_constraints_text = st.text_area(
                "Non-negotiable requirements",
                value=_profile_list_text(
                    profile_value,
                    "hard_constraints",
                ),
                height="content",
                help="Enter one requirement per line.",
                key=profile_widget_key(
                    st.session_state,
                    "hard_constraints",
                ),
            )

        st.markdown(
            "#### Goals and notes"
        )

        left_column, right_column = st.columns(
            2
        )

        with left_column:
            career_goals_text = st.text_area(
                "Career goals",
                value=_profile_list_text(
                    profile_value,
                    "career_goals",
                ),
                height="content",
                help="Enter one goal per line.",
                key=profile_widget_key(
                    st.session_state,
                    "career_goals",
                ),
            )

        with right_column:
            notes_text = st.text_area(
                "Notes and uncertainties",
                value=_profile_list_text(
                    profile_value,
                    "notes",
                ),
                height="content",
                help="Enter one note per line.",
                key=profile_widget_key(
                    st.session_state,
                    "notes",
                ),
            )

        confirmed = st.form_submit_button(
            "Save and confirm profile",
            type="primary",
            width="stretch",
        )

    if confirmed:
        workspace = _get_or_create_workspace()

        try:
            with st.spinner(
                "Saving your reviewed profile..."
            ):
                result = service.confirm_profile(
                    profile=profile_value,
                    profile_edits={
                        "target_roles": (
                            target_roles_text.splitlines()
                        ),
                        "skills": (
                            skills_text.splitlines()
                        ),
                        "experience_level": (
                            experience_level
                        ),
                        "preferred_locations": (
                            preferred_locations_text.splitlines()
                        ),
                        "preferred_work_types": (
                            preferred_work_types_text.splitlines()
                        ),
                        "liked_areas": (
                            liked_areas_text.splitlines()
                        ),
                        "disliked_areas": (
                            disliked_areas_text.splitlines()
                        ),
                        "hard_constraints": (
                            hard_constraints_text.splitlines()
                        ),
                        "career_goals": (
                            career_goals_text.splitlines()
                        ),
                        "notes": (
                            notes_text.splitlines()
                        ),
                    },
                    workspace=workspace,
                )

                record_profile_confirmation(
                    st.session_state,
                    profile=result.review.profile,
                    job_queries=result.job_queries,
                )

        except Exception as error:
            _render_error(error)

    current_profile = st.session_state.get(
        PROFILE_KEY
    )

    if isinstance(current_profile, dict):
        with st.expander(
            "View profile data"
        ):
            st.json(current_profile)

        st.download_button(
            "Download profile data",
            data=(
                json.dumps(
                    current_profile,
                    indent=2,
                    ensure_ascii=False,
                )
                + "\n"
            ),
            file_name="career_profile.json",
            mime="application/json",
        )


def _default_search_location(
    profile: Mapping[str, object],
) -> str:
    """Return the first confirmed preferred location when available."""
    preferred_locations = profile.get(
        "preferred_locations"
    )

    if not isinstance(
        preferred_locations,
        list,
    ):
        return ""

    for location in preferred_locations:
        if (
            isinstance(location, str)
            and location.strip()
        ):
            return location.strip()

    return ""


def _saved_search_setting(
    field_name: str,
    default: object,
) -> object:
    """Return a previously completed search setting when available."""
    settings = st.session_state.get(
        JOB_SEARCH_SETTINGS_KEY
    )

    if not isinstance(settings, dict):
        return default

    return settings.get(
        field_name,
        default,
    )


def _job_preview_rows(
    jobs: Sequence[Mapping[str, object]],
) -> list[dict[str, object]]:
    """Build readable rows for the job-listing preview."""
    rows: list[dict[str, object]] = []

    for job in jobs:
        rows.append(
            {
                "Title": (
                    job.get("title")
                    or "Not provided"
                ),
                "Company": (
                    job.get("company")
                    or "Not provided"
                ),
                "Location": (
                    job.get("location")
                    or "Not provided"
                ),
                "Work type": (
                    job.get("work_type")
                    or "Not provided"
                ),
                "Seniority": (
                    job.get("seniority")
                    or "Not provided"
                ),
            }
        )

    return rows


def _render_collected_jobs() -> None:
    """Render a readable preview of the latest collected jobs."""
    jobs_value = st.session_state.get(
        COLLECTED_JOBS_KEY
    )

    if not isinstance(jobs_value, list):
        return

    st.divider()
    st.subheader("Job listings found")

    if not jobs_value:
        st.warning(
            "No job listings matched the current search. "
            "Try changing the roles, location, or result limit."
        )
        return

    st.success(
        f"{len(jobs_value)} unique job listings are ready."
    )

    preview_rows = _job_preview_rows(
        jobs_value
    )

    st.dataframe(
        preview_rows,
        width="stretch",
        hide_index=True,
    )

    st.download_button(
        "Download job listings",
        data=(
            json.dumps(
                jobs_value,
                indent=2,
                ensure_ascii=False,
            )
            + "\n"
        ),
        file_name="jobs.json",
        mime="application/json",
    )

    st.info(
        "Use the ranking section below to compare and explain "
        "these jobs."
    )


def _render_job_search(
    *,
    service: CareerVoiceWorkflowService,
    search_available: bool,
    capabilities: CapabilityStatus,
) -> None:
    """Render job-search configuration and collection."""
    if (
        st.session_state.get(
            PROFILE_CONFIRMED_KEY
        )
        is not True
    ):
        return

    profile_value = st.session_state.get(
        PROFILE_KEY
    )

    confirmed_roles = st.session_state.get(
        JOB_QUERIES_KEY
    )

    if not isinstance(
        profile_value,
        dict,
    ):
        return

    if not isinstance(
        confirmed_roles,
        tuple,
    ):
        return

    st.divider()
    st.subheader(
        "Configure your job search"
    )

    st.success(
        "Your career profile has been saved and confirmed."
    )

    if not capabilities.job_collection_available:
        st.warning(
            "Live job search is not currently available for this "
            "application. Your confirmed career profile will remain "
            "available."
        )

    st.write(
        "Review the roles and search settings below, then start the job "
        "search. Each role is searched separately."
    )

    default_roles = _saved_search_setting(
        "roles",
        list(confirmed_roles),
    )

    if isinstance(default_roles, list):
        default_role_values = [
            role
            for role in default_roles
            if isinstance(role, str)
        ]
    else:
        default_role_values = [
            role
            for role in confirmed_roles
            if isinstance(role, str)
        ]

    default_roles_text = "\n".join(
        default_role_values[:MAX_JOB_QUERIES]
    )

    default_location = _saved_search_setting(
        "location",
        _default_search_location(
            profile_value
        ),
    )

    if not isinstance(
        default_location,
        str,
    ):
        default_location = ""

    default_max_results = _saved_search_setting(
        "max_results_per_role",
        5,
    )

    if (
        not isinstance(default_max_results, int)
        or isinstance(default_max_results, bool)
        or not 1
        <= default_max_results
        <= MAX_JOB_RESULTS_PER_QUERY
    ):
        default_max_results = min(
            5,
            MAX_JOB_RESULTS_PER_QUERY,
        )

    with st.form("job_search_form"):
        roles_text = st.text_area(
            "Roles to search for",
            value=default_roles_text,
            height="content",
            help=(
                f"Enter up to {MAX_JOB_QUERIES} roles, "
                "one role per line."
            ),
            key=job_search_widget_key(
                st.session_state,
                "roles",
            ),
        )

        st.caption(
            f"You can search up to {MAX_JOB_QUERIES} roles at a time."
        )

        location_column, limit_column, source_column = st.columns(
            3,
            gap="medium",
        )

        with location_column:
            location = st.text_input(
                "Search location (optional)",
                value=default_location,
                placeholder="Example: Adelaide",
                key=job_search_widget_key(
                    st.session_state,
                    "location",
                ),
            )

        with limit_column:
            max_results_per_role = st.number_input(
                "Maximum listings per role",
                min_value=1,
                max_value=MAX_JOB_RESULTS_PER_QUERY,
                value=default_max_results,
                step=1,
                help=(
                    "This limit applies separately to each role before "
                    "duplicate listings are removed. "
                    f"Maximum {MAX_JOB_RESULTS_PER_QUERY} listings per role."
                ),
                key=job_search_widget_key(
                    st.session_state,
                    "max_results",
                ),
            )

        with source_column:
            source = st.selectbox(
                "Job listing provider",
                options=(
                    "adzuna",
                ),
                format_func=lambda value: {
                    "adzuna": "Adzuna",
                }[value],
                key=job_search_widget_key(
                    st.session_state,
                    "source",
                ),
            )

            st.caption(
                "The first web MVP currently searches Adzuna. "
                "Additional providers can be added later."
            )

        search_submitted = st.form_submit_button(
            "Search for jobs",
            type="primary",
            disabled=(
                not search_available
                or not capabilities.job_collection_available
            ),
            width="stretch",
        )

    if search_submitted:
        workspace = _get_or_create_workspace()

        try:
            with st.status(
                "Searching for job listings...",
                expanded=True,
            ) as status:
                st.write(
                    "Searching each role using your confirmed location "
                    "and result limit."
                )

                result = service.search_jobs(
                    roles=roles_text.splitlines(),
                    location=location,
                    max_results_per_role=int(
                        max_results_per_role
                    ),
                    source=source,
                    workspace=workspace,
                )

                st.write(
                    "Combining the results and removing duplicate listings."
                )

                record_job_search(
                    st.session_state,
                    settings=(
                        result.settings.to_state_dict()
                    ),
                    jobs=result.jobs,
                )

                status.update(
                    label=(
                        "Job search complete: "
                        f"{len(result.jobs)} unique listings found."
                    ),
                    state="complete",
                    expanded=False,
                )

        except Exception as error:
            _render_error(error)

    _render_collected_jobs()


def main() -> None:
    """Render the CareerVoice AI web application."""
    st.set_page_config(
        page_title="CareerVoice AI",
        page_icon="💼",
        layout="wide",
    )

    try:
        login_controller = build_login_controller(
            state=st.session_state,
        )
    except Exception:
        LOGGER.exception(
            "Unable to initialize authentication."
        )

        st.title("CareerVoice AI")

        st.error(
            "Sign-in is temporarily unavailable. "
            "Please contact the application administrator."
        )
        return

    if not login_controller.is_authenticated:
        _render_login(
            login_controller
        )
        return

    clear_login_form_state(
        st.session_state
    )

    _render_account_controls(
        login_controller
    )

    app_user = login_controller.current_user

    if app_user is None:
        st.error(
            "Your session could not be verified. "
            "Please sign in again."
        )
        return

    st.title("CareerVoice AI")

    st.write(
        "Turn your career preferences into structured, explainable "
        "job recommendations."
    )

    ai_usage_budget = build_ai_usage_budget(
        state=st.session_state,
        app_user=app_user,
    )

    service = CareerVoiceWorkflowService(
        Repo4OrchestratorGateway(),
        voice_transcriber=Repo1VoiceTranscriber(),
        ai_usage_budget=ai_usage_budget,
    )

    missing_commands = (
        _render_runtime_status()
    )

    capabilities = (
        get_capability_status()
    )

    _render_profile_input(
        service=service,
        extraction_available=(
            "career-profile-extract"
            not in missing_commands
        ),
        capabilities=capabilities,
    )

    _render_profile_review(
        service=service,
    )

    _render_job_search(
        service=service,
        search_available=(
            "job-collect"
            not in missing_commands
        ),
        capabilities=capabilities,
    )

    render_recommendation_workflow(
        service=service,
        ranking_available=(
            "job-recommend"
            not in missing_commands
        ),
        ai_available=(
            capabilities.ai_features_available
        ),
        get_workspace=(
            _get_or_create_workspace
        ),
        render_error=_render_error,
    )

    _render_ai_usage_status(
        ai_usage_budget
    )