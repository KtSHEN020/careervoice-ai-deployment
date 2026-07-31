from typing import Any, Protocol

from pydantic import BaseModel, ConfigDict

from voice_career_profile_extractor.config import create_openai_client
from voice_career_profile_extractor.models import CareerProfile

DEFAULT_LLM_MODEL = "gpt-5.4-mini"

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


class LLMCareerProfile(BaseModel):
    """
    Structured output schema returned by the LLM.
    """

    model_config = ConfigDict(extra="forbid")

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
    ) -> Any:
        """Request and parse a structured response."""


class OpenAIClient(Protocol):
    """
    Protocol for an OpenAI-compatible client.
    """

    responses: ResponsesAPI


def extract_career_profile_with_llm(
    text: str,
    *,
    client: OpenAIClient | None = None,
    model: str = DEFAULT_LLM_MODEL,
) -> CareerProfile:
    """
    Extract a career profile from text using an OpenAI model.
    """
    cleaned_text = text.strip()

    if not cleaned_text:
        raise ValueError("Career profile input text is empty.")

    api_client = client or create_openai_client()

    response = api_client.responses.parse(
        model=model,
        input=[
            {
                "role": "developer",
                "content": EXTRACTION_INSTRUCTIONS,
            },
            {
                "role": "user",
                "content": cleaned_text,
            },
        ],
        text_format=LLMCareerProfile,
    )

    parsed_profile = response.output_parsed

    if parsed_profile is None:
        raise RuntimeError("LLM response did not include a parsed career profile.")

    return CareerProfile(**parsed_profile.model_dump())
