from typing import Any

import pytest

from voice_career_profile_extractor.llm_extractor import (
    DEFAULT_LLM_MODEL,
    MAX_LLM_OUTPUT_TOKENS,
    LLMCareerProfile,
    extract_career_profile_with_llm,
)
from voice_career_profile_extractor.models import CareerProfile


class FakeResponse:
    def __init__(self, parsed_profile: LLMCareerProfile | None) -> None:
        self.output_parsed = parsed_profile


class FakeResponsesAPI:
    def __init__(self, parsed_profile: LLMCareerProfile | None) -> None:
        self.parsed_profile = parsed_profile
        self.received_arguments: dict[str, Any] = {}

    def parse(self, **kwargs: Any) -> FakeResponse:
        self.received_arguments = kwargs
        return FakeResponse(self.parsed_profile)


class FakeOpenAIClient:
    def __init__(self, parsed_profile: LLMCareerProfile | None) -> None:
        self.responses = FakeResponsesAPI(parsed_profile)


def create_sample_llm_profile() -> LLMCareerProfile:
    return LLMCareerProfile(
        target_roles=["junior backend developer"],
        skills=["Python", "SQL", "Git"],
        experience_level="junior",
        preferred_locations=["Adelaide"],
        preferred_work_types=["hybrid"],
        liked_areas=["backend development", "AI"],
        disliked_areas=["sales"],
        hard_constraints=["avoid sales roles"],
        career_goals=["move toward software engineering"],
        notes=[],
    )


def test_extract_career_profile_with_llm_returns_career_profile():
    client = FakeOpenAIClient(create_sample_llm_profile())

    profile = extract_career_profile_with_llm(
        "I want a junior backend role in Adelaide.",
        client=client,
    )

    assert isinstance(profile, CareerProfile)
    assert profile.target_roles == ["junior backend developer"]
    assert profile.skills == ["Python", "SQL", "Git"]
    assert profile.experience_level == "junior"
    assert profile.preferred_locations == ["Adelaide"]
    assert profile.preferred_work_types == ["hybrid"]
    assert profile.disliked_areas == ["sales"]


def test_extract_career_profile_with_llm_sends_expected_request():
    client = FakeOpenAIClient(create_sample_llm_profile())

    extract_career_profile_with_llm(
        "I want a junior backend role.",
        client=client,
    )

    received_arguments = client.responses.received_arguments

    assert received_arguments["model"] == DEFAULT_LLM_MODEL
    assert received_arguments["text_format"] is LLMCareerProfile
    assert (
        received_arguments["max_output_tokens"]
        == MAX_LLM_OUTPUT_TOKENS
    )
    assert received_arguments["input"][0]["role"] == "developer"
    assert received_arguments["input"][1] == {
        "role": "user",
        "content": "I want a junior backend role.",
    }


def test_extract_career_profile_with_llm_uses_custom_model():
    client = FakeOpenAIClient(create_sample_llm_profile())

    extract_career_profile_with_llm(
        "I want a junior backend role.",
        client=client,
        model="custom-model",
    )

    assert client.responses.received_arguments["model"] == "custom-model"


def test_extract_career_profile_with_llm_rejects_empty_text():
    client = FakeOpenAIClient(create_sample_llm_profile())

    with pytest.raises(ValueError, match="Career profile input text is empty."):
        extract_career_profile_with_llm("   ", client=client)


def test_extract_career_profile_with_llm_rejects_missing_parsed_output():
    client = FakeOpenAIClient(None)

    with pytest.raises(
        RuntimeError,
        match="LLM response did not include a parsed career profile.",
    ):
        extract_career_profile_with_llm(
            "I want a software role.",
            client=client,
        )


def test_extract_career_profile_with_llm_requests_simplified_chinese():
    client = FakeOpenAIClient(
        create_sample_llm_profile()
    )

    extract_career_profile_with_llm(
        "I want a junior backend role.",
        client=client,
        output_language="zh-CN",
    )

    developer_message = (
        client.responses
        .received_arguments[
            "input"
        ][0]["content"]
    )

    assert (
        "Simplified Chinese"
        in developer_message
    )

    assert (
        "target_roles"
        in developer_message
    )

    assert (
        "downstream job search"
        in developer_message
    )


def test_extract_career_profile_with_llm_defaults_to_english():
    client = FakeOpenAIClient(
        create_sample_llm_profile()
    )

    extract_career_profile_with_llm(
        "I want a junior backend role.",
        client=client,
    )

    developer_message = (
        client.responses
        .received_arguments[
            "input"
        ][0]["content"]
    )

    assert (
        "Use English"
        in developer_message
    )


def test_extract_career_profile_with_llm_rejects_unknown_output_language():
    client = FakeOpenAIClient(
        create_sample_llm_profile()
    )

    with pytest.raises(
        ValueError,
        match="output_language must be one of",
    ):
        extract_career_profile_with_llm(
            "I want a software role.",
            client=client,
            output_language="fr",
        )