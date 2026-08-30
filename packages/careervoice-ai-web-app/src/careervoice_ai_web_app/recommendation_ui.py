from __future__ import annotations

import json
from collections.abc import Callable, Mapping

import streamlit as st

from careervoice_ai_web_app.i18n import (
    get_app_language,
    translate,
)
from careervoice_ai_web_app.public_limits import (
    MAX_RECOMMENDATIONS,
)
from careervoice_ai_web_app.session_workspace import (
    SessionWorkspace,
)
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

WorkspaceProvider = Callable[
    [],
    SessionWorkspace,
]
ErrorRenderer = Callable[
    [Exception],
    None,
]


def _t(
    key: str,
    **values: object,
) -> str:
    """Translate recommendation UI text."""
    return translate(
        get_app_language(
            st.session_state
        ),
        key,
        **values,
    )


def _localized_recommendation_widget_key(
    field_name: str,
) -> str:
    """
    Return a widget key scoped to the current UI language.

    Internal widget values remain stable identifiers such as
    'rules' and 'llm', while changing language creates a fresh
    presentation-layer widget.
    """
    base_key = recommendation_widget_key(
        st.session_state,
        field_name,
    )

    language = get_app_language(
        st.session_state
    )

    return (
        f"{base_key}_{language.value}"
    )


def _saved_recommendation_setting(
    field_name: str,
    default: object,
) -> object:
    """Return a previously completed ranking setting when available."""
    settings = st.session_state.get(
        RECOMMENDATION_SETTINGS_KEY
    )

    if not isinstance(
        settings,
        dict,
    ):
        return default

    return settings.get(
        field_name,
        default,
    )


def _recommendation_level_label(
    value: object,
) -> str:
    """Return a localized recommendation-level label."""
    if not isinstance(
        value,
        str,
    ):
        return _t(
            "recommendation.level.default"
        )

    cleaned_value = (
        value.strip()
        .lower()
        .replace(
            "-",
            "_",
        )
        .replace(
            " ",
            "_",
        )
    )

    if not cleaned_value:
        return _t(
            "recommendation.level.default"
        )

    translation_key = (
        "recommendation.level."
        f"{cleaned_value}"
    )

    try:
        return _t(
            translation_key
        )
    except KeyError:
        return (
            value.strip()
            .replace(
                "_",
                " ",
            )
            .replace(
                "-",
                " ",
            )
            .title()
        )


def _string_items(
    value: object,
) -> list[str]:
    """Return non-empty strings from a recommendation list field."""
    if not isinstance(
        value,
        list,
    ):
        return []

    return [
        item.strip()
        for item in value
        if (
            isinstance(
                item,
                str,
            )
            and item.strip()
        )
    ]


def _render_list_section(
    heading: str,
    values: object,
) -> None:
    """Render one detail section only when it contains information."""
    items = _string_items(
        values
    )

    if not items:
        return

    st.markdown(
        f"**{heading}**"
    )

    st.markdown(
        "\n".join(
            f"- {item}"
            for item in items
        )
    )


def _matched_skills(
    recommendation: Mapping[
        str,
        object,
    ],
) -> list[str]:
    """Read matched skills from structured recommendation details."""
    matched_details = (
        recommendation.get(
            "matched_details"
        )
    )

    if not isinstance(
        matched_details,
        Mapping,
    ):
        return []

    return _string_items(
        matched_details.get(
            "matched_skills"
        )
    )


def _render_recommendation_card(
    recommendation: Mapping[
        str,
        object,
    ],
    *,
    rank: int,
) -> None:
    """Render one localized ranked recommendation card."""
    title = recommendation.get(
        "title"
    )

    company = recommendation.get(
        "company"
    )

    match_score = recommendation.get(
        "match_score"
    )

    display_title = (
        title.strip()
        if (
            isinstance(
                title,
                str,
            )
            and title.strip()
        )
        else _t(
            "recommendation.card.untitled"
        )
    )

    display_company = (
        company.strip()
        if (
            isinstance(
                company,
                str,
            )
            and company.strip()
        )
        else _t(
            "recommendation.card.company_missing"
        )
    )

    display_score = (
        match_score
        if (
            isinstance(
                match_score,
                int,
            )
            and not isinstance(
                match_score,
                bool,
            )
        )
        else 0
    )

    rejected = (
        recommendation.get(
            "is_rejected_by_constraints"
        )
        is True
    )

    with st.container(
        border=True
    ):
        recommendation_level = (
            _recommendation_level_label(
                recommendation.get(
                    "recommendation_level"
                )
            )
        )

        with st.container(
            horizontal=True,
            horizontal_alignment=(
                "distribute"
            ),
            vertical_alignment="center",
            gap="medium",
        ):
            with st.container():
                st.markdown(
                    f"### {rank}. "
                    f"{display_title}"
                )

                st.caption(
                    display_company
                )

                st.caption(
                    _t(
                        "recommendation.card.level"
                    )
                    + ": "
                    + recommendation_level
                )

            st.metric(
                _t(
                    "recommendation.card.match_score"
                ),
                f"{display_score}/100",
            )

        if rejected:
            st.error(
                _t(
                    "recommendation.card.rejected"
                )
            )

        matched_skills = (
            _matched_skills(
                recommendation
            )
        )

        if matched_skills:
            st.markdown(
                "**"
                + _t(
                    "recommendation.card.matching_skills"
                )
                + "**"
            )

            st.write(
                ", ".join(
                    matched_skills
                )
            )

        _render_list_section(
            _t(
                "recommendation.card.reasons"
            ),
            recommendation.get(
                "reasons"
            ),
        )

        _render_list_section(
            _t(
                "recommendation.card.missing_skills"
            ),
            recommendation.get(
                "missing_skills"
            ),
        )

        _render_list_section(
            _t(
                "recommendation.card.penalties"
            ),
            recommendation.get(
                "penalties"
            ),
        )

        _render_list_section(
            _t(
                "recommendation.card.uncertainties"
            ),
            recommendation.get(
                "uncertainties"
            ),
        )

        score_breakdown = (
            recommendation.get(
                "score_breakdown"
            )
        )

        matched_details = (
            recommendation.get(
                "matched_details"
            )
        )

        if (
            isinstance(
                score_breakdown,
                Mapping,
            )
            and score_breakdown
        ):
            with st.expander(
                _t(
                    "recommendation.card.score_details"
                )
            ):
                st.json(
                    dict(
                        score_breakdown
                    )
                )

        if (
            isinstance(
                matched_details,
                Mapping,
            )
            and matched_details
        ):
            with st.expander(
                _t(
                    "recommendation.card.match_details"
                )
            ):
                st.json(
                    dict(
                        matched_details
                    )
                )


def _ranking_method_label(
    value: object,
) -> str:
    """Return a localized recommendation-method label."""
    labels = {
        "rules": _t(
            "recommendation.method.standard_short"
        ),
        "llm": _t(
            "recommendation.method.ai_short"
        ),
    }

    if not isinstance(
        value,
        str,
    ):
        return _t(
            "recommendation.method.unknown"
        )

    return labels.get(
        value.strip().lower(),
        _t(
            "recommendation.method.unknown"
        ),
    )


def render_recommendation_results() -> None:
    """Render the latest localized recommendation document."""
    document_value = (
        st.session_state.get(
            RECOMMENDATIONS_KEY
        )
    )

    if not isinstance(
        document_value,
        dict,
    ):
        return

    recommendations = (
        document_value.get(
            "recommendations"
        )
    )

    if not isinstance(
        recommendations,
        list,
    ):
        return

    st.divider()

    st.subheader(
        _t(
            "recommendation.results.title"
        )
    )

    total_jobs_scored = (
        document_value.get(
            "total_jobs_scored",
            0,
        )
    )

    total_returned = (
        document_value.get(
            "total_recommendations_returned",
            len(
                recommendations
            ),
        )
    )

    scoring_method = (
        _ranking_method_label(
            document_value.get(
                "scoring_method"
            )
        )
    )

    with st.container(
        horizontal=True,
        gap="medium",
    ):
        st.metric(
            _t(
                "recommendation.results.jobs_compared"
            ),
            total_jobs_scored,
        )

        st.metric(
            _t(
                "recommendation.results.shown"
            ),
            total_returned,
        )

        st.metric(
            _t(
                "recommendation.results.method"
            ),
            scoring_method,
        )

    if not recommendations:
        st.warning(
            _t(
                "recommendation.results.none"
            )
        )

    else:
        st.success(
            _t(
                "recommendation.results.ready",
                count=len(
                    recommendations
                ),
            )
        )

        for (
            rank,
            recommendation,
        ) in enumerate(
            recommendations,
            start=1,
        ):
            if not isinstance(
                recommendation,
                Mapping,
            ):
                continue

            _render_recommendation_card(
                recommendation,
                rank=rank,
            )

    st.download_button(
        _t(
            "recommendation.results.download"
        ),
        data=(
            json.dumps(
                document_value,
                indent=2,
                ensure_ascii=False,
            )
            + "\n"
        ),
        file_name=(
            "recommendations.json"
        ),
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
    """Render localized ranking configuration and results."""
    jobs_value = (
        st.session_state.get(
            COLLECTED_JOBS_KEY
        )
    )

    if not isinstance(
        jobs_value,
        list,
    ):
        return

    if not jobs_value:
        return

    st.divider()

    st.subheader(
        _t(
            "recommendation.workflow.title"
        )
    )

    st.write(
        _t(
            "recommendation.workflow.intro"
        )
    )

    maximum_available = min(
        MAX_RECOMMENDATIONS,
        len(
            jobs_value
        ),
    )

    default_max_results = (
        _saved_recommendation_setting(
            "max_results",
            min(
                5,
                maximum_available,
            ),
        )
    )

    if (
        not isinstance(
            default_max_results,
            int,
        )
        or not 1
        <= default_max_results
        <= maximum_available
    ):
        default_max_results = min(
            5,
            maximum_available,
        )

    default_scorer = (
        _saved_recommendation_setting(
            "scorer",
            "rules",
        )
    )

    if default_scorer not in (
        "rules",
        "llm",
    ):
        default_scorer = (
            "rules"
        )

    if (
        default_scorer == "llm"
        and not ai_available
    ):
        default_scorer = (
            "rules"
        )

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
        default_exclude_rejected = (
            False
        )

    with st.form(
        "recommendation_form"
    ):
        ranking_options = (
            (
                "rules",
                "llm",
            )
            if ai_available
            else (
                "rules",
            )
        )

        ranking_method = (
            st.selectbox(
                _t(
                    "recommendation.method.label"
                ),
                options=(
                    ranking_options
                ),
                index=(
                    ranking_options.index(
                        default_scorer
                    )
                ),
                format_func=(
                    lambda value: {
                        "rules": _t(
                            "recommendation.method.standard"
                        ),
                        "llm": _t(
                            "recommendation.method.ai"
                        ),
                    }[value]
                ),
                key=(
                    _localized_recommendation_widget_key(
                        "scorer"
                    )
                ),
            )
        )

        if ai_available:
            st.caption(
                _t(
                    "recommendation.method.help_available"
                )
            )

        else:
            st.caption(
                _t(
                    "recommendation.method.help_unavailable"
                )
            )

        (
            left_column,
            right_column,
        ) = st.columns(
            2
        )

        with left_column:
            max_results = (
                st.number_input(
                    _t(
                        "recommendation.max_results"
                    ),
                    min_value=1,
                    max_value=(
                        maximum_available
                    ),
                    value=(
                        default_max_results
                    ),
                    step=1,
                    help=_t(
                        "recommendation.max_results_help",
                        max_results=(
                            MAX_RECOMMENDATIONS
                        ),
                    ),
                    key=(
                        _localized_recommendation_widget_key(
                            "max_results"
                        )
                    ),
                )
            )

        with right_column:
            exclude_rejected = (
                st.checkbox(
                    _t(
                        "recommendation.hide_rejected"
                    ),
                    value=(
                        default_exclude_rejected
                    ),
                    key=(
                        _localized_recommendation_widget_key(
                            "exclude_rejected"
                        )
                    ),
                )
            )

        submitted = (
            st.form_submit_button(
                _t(
                    "recommendation.generate"
                ),
                type="primary",
                disabled=(
                    not ranking_available
                ),
                width="stretch",
            )
        )

    if submitted:
        workspace = (
            get_workspace()
        )

        try:
            with st.status(
                _t(
                    "recommendation.ranking"
                ),
                expanded=True,
            ) as status:
                st.write(
                    _t(
                        "recommendation.comparing"
                    )
                )

                result = (
                    service.rank_jobs(
                        scorer=(
                            ranking_method
                        ),
                        max_results=int(
                            max_results
                        ),
                        exclude_rejected=(
                            exclude_rejected
                        ),
                        workspace=(
                            workspace
                        ),
                    )
                )

                st.write(
                    _t(
                        "recommendation.preparing"
                    )
                )

                record_recommendations(
                    st.session_state,
                    settings=(
                        result.settings
                        .to_state_dict()
                    ),
                    document=(
                        result.document
                        .document
                    ),
                )

                recommendation_count = (
                    result.document
                    .total_recommendations_returned
                )

                status.update(
                    label=_t(
                        "recommendation.ready_status",
                        count=(
                            recommendation_count
                        ),
                    ),
                    state="complete",
                    expanded=False,
                )

        except Exception as error:
            render_error(
                error
            )

    render_recommendation_results()