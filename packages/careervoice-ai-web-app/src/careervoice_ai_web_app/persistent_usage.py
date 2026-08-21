"""Provider-independent persistent usage models for CareerVoice AI."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from enum import StrEnum
from typing import Protocol

from careervoice_ai_web_app.user_models import AppUser


class UsageOperation(StrEnum):
    """Operations tracked by CareerVoice persistent usage."""

    PROFILE_EXTRACTION = "profile_extraction"
    VOICE_TRANSCRIPTION = "voice_transcription"
    DOCUMENT_RECOGNITION = "document_recognition"
    AI_RANKING = "ai_ranking"
    JOB_SEARCH = "job_search"


@dataclass(frozen=True)
class DailyUsageSnapshot:
    """Persisted usage counters for one CareerVoice user and date."""

    user_id: object
    usage_date: date
    ai_units_used: int
    ai_profile_extractions: int
    voice_transcriptions: int
    document_recognitions: int
    ai_ranking_runs: int
    job_searches: int


@dataclass(frozen=True)
class UsageDecision:
    """Result of attempting to record and consume usage."""

    allowed: bool
    ai_units_used: int
    remaining_ai_units: int


class PersistentUsageRepository(Protocol):
    """Persistence operations required for user-level usage controls."""

    def get_daily_usage(
        self,
        *,
        user: AppUser,
        usage_date: date,
    ) -> DailyUsageSnapshot:
        """Return the user's persisted counters for one date."""
        ...

    def consume(
        self,
        *,
        user: AppUser,
        usage_date: date,
        units: int,
        daily_limit: int,
        operation: UsageOperation,
    ) -> UsageDecision:
        """Atomically record an operation and consume usage if allowed."""
        ...