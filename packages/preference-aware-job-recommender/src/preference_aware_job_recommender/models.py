from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


AlignmentLevel = Literal[
    "strong",
    "partial",
    "weak",
    "none",
    "unclear",
]


class LLMJobEvaluation(BaseModel):
    """
    Structured semantic job evaluation returned by an LLM.
    """

    model_config = ConfigDict(extra="forbid")

    job_id: str
    match_score: int = Field(ge=0, le=100)
    role_alignment: AlignmentLevel
    career_goal_alignment: AlignmentLevel
    matched_skills: list[str]
    missing_skills: list[str]
    reasons: list[str]
    penalties: list[str]
    hard_constraint_conflicts: list[str]
    uncertainties: list[str]