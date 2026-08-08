from __future__ import annotations

import json
from typing import Any, Protocol

from preference_aware_job_recommender.config import create_openai_client
from preference_aware_job_recommender.models import LLMJobEvaluation
from preference_aware_job_recommender.scoring import get_recommendation_level


DEFAULT_LLM_MODEL = "gpt-5.4-mini"
MAX_LLM_OUTPUT_TOKENS = 1200

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
- Treat hard constraints strictly and list every detected conflict.
- Add concise penalties for relevant concerns.
- Add uncertainties when the listing does not provide enough information.
- Keep reasons, penalties, and uncertainties concise.
- Return the job_id exactly as provided in the job listing.
""".strip()


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


def _merge_unique(items: list[str]) -> list[str]:
    """
    Return strings in their original order without duplicates.
    """
    unique_items = []

    for item in items:
        if item not in unique_items:
            unique_items.append(item)

    return unique_items


def score_job_with_llm(
    profile: dict[str, Any],
    job: dict[str, Any],
    *,
    client: OpenAIClient | None = None,
    model: str = DEFAULT_LLM_MODEL,
) -> dict[str, Any]:
    """
    Score one structured job against a career profile using an LLM.
    """
    job_id = str(job.get("job_id", "")).strip()

    if not job_id:
        raise ValueError("Job must include a non-empty job_id.")

    api_client = client or create_openai_client()

    response = api_client.responses.parse(
        model=model,
        input=[
            {
                "role": "developer",
                "content": LLM_SCORING_INSTRUCTIONS,
            },
            {
                "role": "user",
                "content": _build_llm_input(profile, job),
            },
        ],
        text_format=LLMJobEvaluation,
        max_output_tokens=MAX_LLM_OUTPUT_TOKENS,
    )

    evaluation = response.output_parsed

    if evaluation is None:
        raise RuntimeError("LLM response did not include a parsed job evaluation.")

    if evaluation.job_id != job_id:
        raise RuntimeError(
            "LLM response job_id does not match the evaluated job."
        )

    hard_constraint_conflicts = evaluation.hard_constraint_conflicts
    is_rejected = bool(hard_constraint_conflicts)

    raw_match_score = evaluation.match_score

    if is_rejected:
        final_match_score = min(raw_match_score, 25)
    else:
        final_match_score = raw_match_score

    hard_constraint_penalties = [
        f"Conflicts with hard constraint: {conflict}"
        for conflict in hard_constraint_conflicts
    ]

    penalties = _merge_unique(
        evaluation.penalties + hard_constraint_penalties
    )

    return {
        "job_id": job_id,
        "title": job.get("title", ""),
        "company": job.get("company", ""),
        "match_score": final_match_score,
        "recommendation_level": get_recommendation_level(
            final_match_score
        ),
        "reasons": evaluation.reasons,
        "missing_skills": evaluation.missing_skills,
        "penalties": penalties,
        "is_rejected_by_constraints": is_rejected,
        "uncertainties": evaluation.uncertainties,
        "scoring_method": "llm",
        "score_breakdown": {
            "llm_semantic_score": raw_match_score,
            "final_score": final_match_score,
            "hard_constraint_score_cap_applied": is_rejected,
        },
        "matched_details": {
            "matched_skills": evaluation.matched_skills,
            "role_alignment": evaluation.role_alignment,
            "career_goal_alignment": evaluation.career_goal_alignment,
            "matched_hard_constraints": hard_constraint_conflicts,
        },
    }