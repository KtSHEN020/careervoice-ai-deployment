import pytest

from careervoice_ai_web_app.ai_usage import (
    AI_USAGE_UNITS_KEY,
    MAX_AI_USAGE_UNITS_PER_SESSION,
    AIUsageLimitError,
    AIUsageStatus,
    SessionAIUsageBudget,
)


def test_ai_usage_budget_starts_with_full_allowance() -> None:
    state: dict[str, object] = {}

    budget = SessionAIUsageBudget(state)

    assert budget.used == 0
    assert (
        budget.remaining
        == MAX_AI_USAGE_UNITS_PER_SESSION
    )


def test_ai_usage_budget_reserves_units() -> None:
    state: dict[str, object] = {}

    budget = SessionAIUsageBudget(state)

    budget.reserve(
        1,
        feature="voice transcription",
    )

    budget.reserve(
        10,
        feature="AI-assisted job ranking",
    )

    assert budget.used == 11
    assert budget.remaining == 29
    assert state[AI_USAGE_UNITS_KEY] == 11


def test_ai_usage_budget_rejects_action_over_remaining_allowance() -> None:
    state: dict[str, object] = {
        AI_USAGE_UNITS_KEY: 35,
    }

    budget = SessionAIUsageBudget(state)

    with pytest.raises(
        AIUsageLimitError,
        match="AI-assisted job ranking",
    ):
        budget.reserve(
            10,
            feature="AI-assisted job ranking",
        )

    assert budget.used == 35
    assert budget.remaining == 5


def test_ai_usage_budget_allows_exact_remaining_allowance() -> None:
    state: dict[str, object] = {
        AI_USAGE_UNITS_KEY: 30,
    }

    budget = SessionAIUsageBudget(state)

    budget.reserve(
        10,
        feature="AI-assisted job ranking",
    )

    assert budget.used == 40
    assert budget.remaining == 0


def test_ai_usage_budget_ignores_invalid_stored_value() -> None:
    state: dict[str, object] = {
        AI_USAGE_UNITS_KEY: "invalid",
    }

    budget = SessionAIUsageBudget(state)

    assert budget.used == 0

    budget.reserve(
        1,
        feature="AI-assisted profile creation",
    )

    assert budget.used == 1


def test_ai_usage_budget_reports_status() -> None:
    state: dict[str, object] = {
        AI_USAGE_UNITS_KEY: 7,
    }

    budget = SessionAIUsageBudget(state)

    assert budget.status() == AIUsageStatus(
        limit=40,
        used=7,
        remaining=33,
    )