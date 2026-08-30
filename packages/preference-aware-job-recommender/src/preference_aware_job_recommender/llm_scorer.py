from __future__ import annotations

import json
from typing import Any, Protocol

from preference_aware_job_recommender.config import (
    create_openai_client,
)
from preference_aware_job_recommender.models import (
    LLMJobEvaluation,
)
from preference_aware_job_recommender.scoring import (
    get_recommendation_level,
)


DEFAULT_LLM_MODEL = "gpt-5.4-mini"
MAX_LLM_OUTPUT_TOKENS = 1200

SUPPORTED_OUTPUT_LANGUAGES = (
    "en",
    "zh-CN",
)

LLM_SCORING_INSTRUCTIONS = """
Evaluate how well one structured job listing matches one structured career profile.

Follow these rules:
- Use only information supported by the career profile and job listing.
- Do not invent skills, preferences, responsibilities, or job conditions.
- Compare meanings, not only exact wording.
- Consider target roles, skills, experience level, preferred locations,
  preferred work types, liked areas, disliked areas, career goals, and hard
  constraints.
- Recognise clearly related or transferable skills when appropriate.
- List important missing skills.
- Treat hard constraints strictly.
- hard_constraint_conflicts must contain only actual conflicts with entries
  from career_profile.hard_constraints.
- Copy each conflicting hard constraint exactly as it appears in
  career_profile.hard_constraints.
- Do not translate, paraphrase, summarize, or invent values in
  hard_constraint_conflicts.
- If career_profile.hard_constraints is empty, hard_constraint_conflicts
  must be an empty list.
- If no hard-constraint conflict exists, return an empty list. Never put
  text such as "none", "no conflict", or an equivalent phrase in that list.
""".strip()


OUTPUT_LANGUAGE_INSTRUCTIONS = {
    "en": """
Write human-readable recommendation explanations in English.

Keep job identifiers, company names, job titles, skill names, and technology
names as provided when appropriate.

The role_alignment and career_goal_alignment fields must still use the exact
schema enum values.
""".strip(),
    "zh-CN": """
Write user-facing recommendation explanations in Simplified Chinese,
including:
- reasons
- penalties
- uncertainties

hard_constraint_conflicts is a machine-readable evidence field. Copy any
conflicting hard constraint exactly as it appears in
career_profile.hard_constraints. Do not translate or paraphrase it.

Keep job_id exactly as supplied.

Preserve company names, job titles, skill names, and technology names as
provided when appropriate rather than translating proper nouns unnecessarily.

The matched_skills and missing_skills fields should retain the actual skill
names from the profile or job listing.

The role_alignment and career_goal_alignment fields must still use the exact
schema enum values required by the structured-output schema.
""".strip(),
}


class ResponsesAPI(Protocol):
    """
    Protocol for an OpenAI-compatible Responses API.
    """

    def parse(
        self,
        *,
        model: str,
        input: list[dict[str, str]],
        text_format: type[LLMJobEvaluation],
        max_output_tokens: int,
    ) -> Any:
        """Request and parse a structured response."""


class OpenAIClient(Protocol):
    """
    Protocol for an OpenAI-compatible client.
    """

    responses: ResponsesAPI


def _normalize_output_language(
    output_language: str,
) -> str:
    """
    Validate and normalize one requested output language.
    """
    if not isinstance(
        output_language,
        str,
    ):
        raise ValueError(
            "output_language must be one of: en, zh-CN."
        )

    cleaned_language = (
        output_language.strip()
    )

    if (
        cleaned_language
        not in SUPPORTED_OUTPUT_LANGUAGES
    ):
        raise ValueError(
            "output_language must be one of: en, zh-CN."
        )

    return cleaned_language


def _build_scoring_instructions(
    output_language: str,
) -> str:
    """
    Build LLM job-scoring instructions for the requested language.
    """
    normalized_language = (
        _normalize_output_language(
            output_language
        )
    )

    return (
        LLM_SCORING_INSTRUCTIONS
        + "\n\nOutput language requirements:\n"
        + OUTPUT_LANGUAGE_INSTRUCTIONS[
            normalized_language
        ]
    )


def _build_llm_input(
    profile: dict[str, Any],
    job: dict[str, Any],
) -> str:
    """
    Build the JSON input sent to the LLM scorer.
    """
    return json.dumps(
        {
            "career_profile": profile,
            "job": job,
        },
        indent=2,
        ensure_ascii=False,
    )


def _merge_unique(
    items: list[str],
) -> list[str]:
    """
    Return strings in their original order without duplicates.
    """
    unique_items = []

    for item in items:
        if item not in unique_items:
            unique_items.append(
                item
            )

    return unique_items


def _hard_constraint_penalty(
    conflict: str,
    *,
    output_language: str,
) -> str:
    """
    Build one language-aware hard-constraint penalty.
    """
    if output_language == "zh-CN":
        return (
            "违反不可妥协要求："
            + conflict
        )

    return (
        "Conflicts with hard constraint: "
        + conflict
    )


def _validated_hard_constraint_conflicts(
    profile: dict[str, Any],
    conflicts: list[str],
) -> list[str]:
    """
    Keep only conflicts that exactly correspond to profile hard constraints.
    """
    value = profile.get(
        "hard_constraints"
    )

    if not isinstance(
        value,
        list,
    ):
        return []

    profile_constraints: dict[
        str,
        str,
    ] = {}

    for item in value:
        if (
            not isinstance(
                item,
                str,
            )
            or not item.strip()
        ):
            continue

        cleaned_item = item.strip()

        normalized_item = " ".join(
            cleaned_item.casefold().split()
        )

        profile_constraints[
            normalized_item
        ] = cleaned_item

    validated: list[str] = []

    for conflict in conflicts:
        if not isinstance(
            conflict,
            str,
        ):
            continue

        normalized_conflict = " ".join(
            conflict.strip().casefold().split()
        )

        matched_constraint = (
            profile_constraints.get(
                normalized_conflict
            )
        )

        if (
            matched_constraint is not None
            and matched_constraint
            not in validated
        ):
            validated.append(
                matched_constraint
            )

    return validated


def score_job_with_llm(
    profile: dict[str, Any],
    job: dict[str, Any],
    *,
    client: OpenAIClient | None = None,
    model: str = DEFAULT_LLM_MODEL,
    output_language: str = "en",
) -> dict[str, Any]:
    """
    Score one structured job against a career profile using an LLM.
    """
    job_id = str(
        job.get(
            "job_id",
            "",
        )
    ).strip()

    if not job_id:
        raise ValueError(
            "Job must include a non-empty job_id."
        )

    normalized_language = (
        _normalize_output_language(
            output_language
        )
    )

    instructions = (
        _build_scoring_instructions(
            normalized_language
        )
    )

    api_client = (
        client
        or create_openai_client()
    )

    response = api_client.responses.parse(
        model=model,
        input=[
            {
                "role": "developer",
                "content": instructions,
            },
            {
                "role": "user",
                "content": _build_llm_input(
                    profile,
                    job,
                ),
            },
        ],
        text_format=LLMJobEvaluation,
        max_output_tokens=MAX_LLM_OUTPUT_TOKENS,
    )

    evaluation = (
        response.output_parsed
    )

    if evaluation is None:
        raise RuntimeError(
            "LLM response did not include a parsed job evaluation."
        )

    if evaluation.job_id != job_id:
        raise RuntimeError(
            "LLM response job_id does not match the evaluated job."
        )

    hard_constraint_conflicts = (
        _validated_hard_constraint_conflicts(
            profile,
            evaluation.hard_constraint_conflicts,
        )
    )

    is_rejected = bool(
        hard_constraint_conflicts
    )

    raw_match_score = (
        evaluation.match_score
    )

    if is_rejected:
        final_match_score = min(
            raw_match_score,
            25,
        )
    else:
        final_match_score = (
            raw_match_score
        )

    hard_constraint_penalties = [
        _hard_constraint_penalty(
            conflict,
            output_language=(
                normalized_language
            ),
        )
        for conflict
        in hard_constraint_conflicts
    ]

    penalties = _merge_unique(
        evaluation.penalties
        + hard_constraint_penalties
    )

    return {
        "job_id": job_id,
        "title": job.get(
            "title",
            "",
        ),
        "company": job.get(
            "company",
            "",
        ),
        "match_score": (
            final_match_score
        ),
        "recommendation_level": (
            get_recommendation_level(
                final_match_score
            )
        ),
        "reasons": (
            evaluation.reasons
        ),
        "missing_skills": (
            evaluation.missing_skills
        ),
        "penalties": penalties,
        "is_rejected_by_constraints": (
            is_rejected
        ),
        "uncertainties": (
            evaluation.uncertainties
        ),
        "scoring_method": "llm",
        "score_breakdown": {
            "llm_semantic_score": (
                raw_match_score
            ),
            "final_score": (
                final_match_score
            ),
            "hard_constraint_score_cap_applied": (
                is_rejected
            ),
        },
        "matched_details": {
            "matched_skills": (
                evaluation.matched_skills
            ),
            "role_alignment": (
                evaluation.role_alignment
            ),
            "career_goal_alignment": (
                evaluation.career_goal_alignment
            ),
            "matched_hard_constraints": (
                hard_constraint_conflicts
            ),
        },
    }