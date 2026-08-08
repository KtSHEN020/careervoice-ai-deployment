from __future__ import annotations

import json
from collections.abc import Callable, Mapping

import streamlit as st

from careervoice_ai_web_app.session_workspace import SessionWorkspace
from careervoice_ai_web_app.ui_state import (
    COLLECTED_JOBS_KEY,
    RECOMMENDATION_SETTINGS_KEY,
    RECOMMENDATIONS_KEY,
    recommendation_widget_key,
    record_recommendations,
)
from careervoice_ai_web_app.workflow_service import (
    CareerVoiceWorkflowService,
)

WorkspaceProvider = Callable[[], SessionWorkspace]
ErrorRenderer = Callable[[Exception], None]


def _saved_recommendation_setting(
    field_name: str,
    default: object,
) -> object:
    """Return a previously completed ranking setting when available."""
    settings = st.session_state.get(RECOMMENDATION_SETTINGS_KEY)

    if not isinstance(settings, dict):
        return default

    return settings.get(field_name, default)


def _display_label(
    value: object,
    *,
    fallback: str,
) -> str:
    """Convert an internal identifier into readable text."""
    if not isinstance(value, str):
        return fallback

    cleaned_value = value.strip()

    if not cleaned_value:
        return fallback

    return (
        cleaned_value.replace("_", " ")
        .replace("-", " ")
        .title()
    )


def _string_items(value: object) -> list[str]:
    """Return non-empty strings from a recommendation list field."""
    if not isinstance(value, list):
        return []

    return [
        item.strip()
        for item in value
        if isinstance(item, str) and item.strip()
    ]


def _render_list_section(
    heading: str,
    values: object,
) -> None:
    """Render one detail section only when it contains information."""
    items = _string_items(values)

    if not items:
        return

    st.markdown(f"**{heading}**")
    st.markdown(
        "\n".join(
            f"- {item}"
            for item in items
        )
    )


def _matched_skills(
    recommendation: Mapping[str, object],
) -> list[str]:
    """Read matched skills from the structured recommendation details."""
    matched_details = recommendation.get("matched_details")

    if not isinstance(matched_details, Mapping):
        return []

    return _string_items(
        matched_details.get("matched_skills")
    )


def _render_recommendation_card(
    recommendation: Mapping[str, object],
    *,
    rank: int,
) -> None:
    """Render one ranked recommendation in a bordered card."""
    title = recommendation.get("title")
    company = recommendation.get("company")
    match_score = recommendation.get("match_score")

    display_title = (
        title.strip()
        if isinstance(title, str) and title.strip()
        else "Untitled job"
    )

    display_company = (
        company.strip()
        if isinstance(company, str) and company.strip()
        else "Company not provided"
    )

    display_score = (
        match_score
        if (
            isinstance(match_score, int)
            and not isinstance(match_score, bool)
        )
        else 0
    )

    rejected = (
        recommendation.get("is_rejected_by_constraints")
        is True
    )

    with st.container(border=True):
        recommendation_level = _display_label(
            recommendation.get("recommendation_level"),
            fallback="Recommendation",
        )

        with st.container(
            horizontal=True,
            horizontal_alignment="distribute",
            vertical_alignment="center",
            gap="medium",
        ):
            with st.container():
                st.markdown(
                    f"### {rank}. {display_title}"
                )
                st.caption(display_company)
                st.caption(
                    f"Recommendation level: {recommendation_level}"
                )

            st.metric(
                "Match score",
                f"{display_score}/100",
            )

        if rejected:
            st.error(
                "This job conflicts with one or more "
                "non-negotiable requirements."
            )

        matched_skills = _matched_skills(
            recommendation
        )

        if matched_skills:
            st.markdown("**Matching skills**")
            st.write(", ".join(matched_skills))

        _render_list_section(
            "Why this job may fit",
            recommendation.get("reasons"),
        )

        _render_list_section(
            "Missing skills",
            recommendation.get("missing_skills"),
        )

        _render_list_section(
            "Penalties and concerns",
            recommendation.get("penalties"),
        )

        _render_list_section(
            "Uncertainties",
            recommendation.get("uncertainties"),
        )

        score_breakdown = recommendation.get(
            "score_breakdown"
        )

        matched_details = recommendation.get(
            "matched_details"
        )

        if (
            isinstance(score_breakdown, Mapping)
            and score_breakdown
        ):
            with st.expander("View score details"):
                st.json(dict(score_breakdown))

        if (
            isinstance(matched_details, Mapping)
            and matched_details
        ):
            with st.expander("View matching details"):
                st.json(dict(matched_details))

def _ranking_method_label(value: object) -> str:
    """Return a user-friendly recommendation method label."""
    labels = {
        "rules": "Standard",
        "llm": "AI-assisted",
    }

    if not isinstance(value, str):
        return "Unknown"

    return labels.get(
        value.strip().lower(),
        "Unknown",
    )

def render_recommendation_results() -> None:
    """Render the latest validated recommendation document."""
    document_value = st.session_state.get(
        RECOMMENDATIONS_KEY
    )

    if not isinstance(document_value, dict):
        return

    recommendations = document_value.get(
        "recommendations"
    )

    if not isinstance(recommendations, list):
        return

    st.divider()
    st.subheader("Recommended jobs")

    total_jobs_scored = document_value.get(
        "total_jobs_scored",
        0,
    )

    total_returned = document_value.get(
        "total_recommendations_returned",
        len(recommendations),
    )

    scoring_method = _ranking_method_label(
        document_value.get("scoring_method")
    )

    with st.container(
        horizontal=True,
        gap="medium",
    ):
        st.metric(
            "Jobs compared",
            total_jobs_scored,
        )

        st.metric(
            "Recommendations shown",
            total_returned,
        )

        st.metric(
            "Ranking method",
            scoring_method,
        )

    if not recommendations:
        st.warning(
            "No recommendations matched the current settings. "
            "Try showing rejected jobs or increasing the "
            "recommendation limit."
        )
    else:
        st.success(
            f"{len(recommendations)} recommendations are ready."
        )

        for rank, recommendation in enumerate(
            recommendations,
            start=1,
        ):
            if not isinstance(recommendation, Mapping):
                continue

            _render_recommendation_card(
                recommendation,
                rank=rank,
            )

    st.download_button(
        "Download recommendations",
        data=(
            json.dumps(
                document_value,
                indent=2,
                ensure_ascii=False,
            )
            + "\n"
        ),
        file_name="recommendations.json",
        mime="application/json",
    )


def render_recommendation_workflow(
    *,
    service: CareerVoiceWorkflowService,
    ranking_available: bool,
    ai_available: bool,
    get_workspace: WorkspaceProvider,
    render_error: ErrorRenderer,
) -> None:
    """Render ranking configuration and recommendation results."""
    jobs_value = st.session_state.get(
        COLLECTED_JOBS_KEY
    )

    if not isinstance(jobs_value, list):
        return

    if not jobs_value:
        return

    st.divider()
    st.subheader("Rank and explain your job matches")

    st.write(
        "Choose how the application should compare the collected "
        "jobs with your confirmed career profile."
    )

    maximum_available = min(
        50,
        len(jobs_value),
    )

    default_max_results = _saved_recommendation_setting(
        "max_results",
        min(5, maximum_available),
    )

    if (
        not isinstance(default_max_results, int)
        or not 1
        <= default_max_results
        <= maximum_available
    ):
        default_max_results = min(
            5,
            maximum_available,
        )

    default_scorer = _saved_recommendation_setting(
        "scorer",
        "rules",
    )

    if default_scorer not in ("rules", "llm"):
        default_scorer = "rules"

    if default_scorer == "llm" and not ai_available:
        default_scorer = "rules"

    default_exclude_rejected = (
        _saved_recommendation_setting(
            "exclude_rejected",
            False,
        )
    )

    if not isinstance(
        default_exclude_rejected,
        bool,
    ):
        default_exclude_rejected = False

    with st.form("recommendation_form"):
        ranking_options = (
            ("rules", "llm")
            if ai_available
            else ("rules",)
        )
        ranking_method = st.selectbox(
            "Ranking method",
            options=ranking_options,
            index=(
                0
                if default_scorer == "rules"
                else 1
            ),
            format_func=lambda value: {
                "rules": "Standard ranking",
                "llm": "AI-assisted ranking",
            }[value],
            key=recommendation_widget_key(
                st.session_state,
                "scorer",
            ),
        )

        if ai_available:
            st.caption(
                "Standard ranking is deterministic and does not use "
                "an external AI service. AI-assisted ranking can provide "
                "more flexible explanations."
            )
        else:
            st.caption(
                "Standard ranking is available. AI-assisted ranking is "
                "not currently available for this application."
            )

        left_column, right_column = st.columns(2)

        with left_column:
            max_results = st.number_input(
                "Maximum recommendations",
                min_value=1,
                max_value=maximum_available,
                value=default_max_results,
                step=1,
                key=recommendation_widget_key(
                    st.session_state,
                    "max_results",
                ),
            )

        with right_column:
            exclude_rejected = st.checkbox(
                "Hide jobs that conflict with "
                "non-negotiable requirements",
                value=default_exclude_rejected,
                key=recommendation_widget_key(
                    st.session_state,
                    "exclude_rejected",
                ),
            )

        submitted = st.form_submit_button(
            "Generate recommendations",
            type="primary",
            disabled=not ranking_available,
            width="stretch",
        )

    if submitted:
        workspace = get_workspace()

        try:
            with st.status(
                "Ranking and explaining the collected jobs...",
                expanded=True,
            ) as status:
                st.write(
                    "Comparing each job with your roles, skills, "
                    "preferences, and non-negotiable requirements."
                )

                result = service.rank_jobs(
                    scorer=ranking_method,
                    max_results=int(max_results),
                    exclude_rejected=exclude_rejected,
                    workspace=workspace,
                )

                st.write(
                    "Preparing readable scores and explanations."
                )

                record_recommendations(
                    st.session_state,
                    settings=(
                        result.settings.to_state_dict()
                    ),
                    document=result.document.document,
                )

                recommendation_count = (
                    result.document.total_recommendations_returned
                )

                status.update(
                    label=(
                        "Recommendations ready: "
                        f"{recommendation_count} jobs ranked."
                    ),
                    state="complete",
                    expanded=False,
                )

        except Exception as error:
            render_error(error)

    render_recommendation_results()