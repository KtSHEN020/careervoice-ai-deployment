from typing import Any, Protocol

from pydantic import BaseModel, ConfigDict

from voice_career_profile_extractor.config import (
    create_openai_client,
)
from voice_career_profile_extractor.models import CareerProfile


DEFAULT_LLM_MODEL = "gpt-5.4-mini"
MAX_LLM_OUTPUT_TOKENS = 2000

SUPPORTED_OUTPUT_LANGUAGES = (
    "en",
    "zh-CN",
)

EXTRACTION_INSTRUCTIONS = """
Extract a structured career profile from the user's text.

Follow these rules:
- Extract only information supported by the user's words.
- Do not invent missing preferences, skills, or experience.
- Use empty lists when a list field is not mentioned.
- Use null when the experience level is unclear.
- Keep general dislikes separate from hard constraints.
- Add a short note when important information is missing or uncertain.
- Keep each list item concise.
""".strip()


OUTPUT_LANGUAGE_INSTRUCTIONS = {
    "en": """
Use English for human-readable career-profile values.

Preserve proper nouns, company names, technology names, and location names
when appropriate.
""".strip(),
    "zh-CN": """
Use Simplified Chinese for user-facing explanatory and preference fields,
especially:
- liked_areas
- disliked_areas
- hard_constraints
- career_goals
- notes

For fields used directly by downstream job search and matching, keep concise
canonical English values when practical:
- target_roles
- skills
- experience_level
- preferred_locations
- preferred_work_types

Preserve proper nouns and technology names when appropriate.

This separation is important because the career profile is also used to search
English-language job listings.
""".strip(),
}


class LLMCareerProfile(BaseModel):
    """
    Structured output schema returned by the LLM.
    """

    model_config = ConfigDict(
        extra="forbid"
    )

    target_roles: list[str]
    skills: list[str]
    experience_level: str | None
    preferred_locations: list[str]
    preferred_work_types: list[str]
    liked_areas: list[str]
    disliked_areas: list[str]
    hard_constraints: list[str]
    career_goals: list[str]
    notes: list[str]


class ResponsesAPI(Protocol):
    """
    Protocol for an OpenAI-compatible Responses API.
    """

    def parse(
        self,
        *,
        model: str,
        input: list[dict[str, str]],
        text_format: type[LLMCareerProfile],
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


def _build_extraction_instructions(
    output_language: str,
) -> str:
    """
    Build profile-extraction instructions for the requested language.
    """
    normalized_language = (
        _normalize_output_language(
            output_language
        )
    )

    return (
        EXTRACTION_INSTRUCTIONS
        + "\n\nOutput language requirements:\n"
        + OUTPUT_LANGUAGE_INSTRUCTIONS[
            normalized_language
        ]
    )


def extract_career_profile_with_llm(
    text: str,
    *,
    client: OpenAIClient | None = None,
    model: str = DEFAULT_LLM_MODEL,
    output_language: str = "en",
) -> CareerProfile:
    """
    Extract a career profile from text using an OpenAI model.
    """
    cleaned_text = text.strip()

    if not cleaned_text:
        raise ValueError(
            "Career profile input text is empty."
        )

    instructions = (
        _build_extraction_instructions(
            output_language
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
                "content": cleaned_text,
            },
        ],
        text_format=LLMCareerProfile,
        max_output_tokens=MAX_LLM_OUTPUT_TOKENS,
    )

    parsed_profile = (
        response.output_parsed
    )

    if parsed_profile is None:
        raise RuntimeError(
            "LLM response did not include a parsed career profile."
        )

    return CareerProfile(
        **parsed_profile.model_dump()
    )