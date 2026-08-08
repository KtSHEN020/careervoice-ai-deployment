from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


WorkType = Literal["remote", "hybrid", "onsite", "unknown"]

Seniority = Literal[
    "intern",
    "junior",
    "mid",
    "senior",
    "lead",
    "unknown",
]


class NormalizedJob(BaseModel):
    """
    A cleaned and normalized job listing compatible with Repo 2.

    Repo 2 mainly uses fields such as title, location, work_type, seniority,
    skills, responsibilities, and tags for recommendation scoring.

    Repo 3 also keeps source metadata so each collected job can be traced
    back to where it came from.
    """

    model_config = ConfigDict(extra="forbid")

    job_id: str = Field(min_length=1)
    title: str = Field(min_length=1)
    company: str = Field(min_length=1)
    location: str = Field(min_length=1)
    work_type: WorkType
    seniority: Seniority
    description: str = Field(min_length=1)
    required_skills: list[str] = Field(default_factory=list)
    preferred_skills: list[str] = Field(default_factory=list)
    responsibilities: list[str] = Field(default_factory=list)
    tags: list[str] = Field(default_factory=list)
    source: str = Field(min_length=1)
    source_url: str = Field(min_length=1)
    collected_at: datetime

    @field_validator(
        "job_id",
        "title",
        "company",
        "location",
        "description",
        "source",
        "source_url",
        mode="before",
    )
    @classmethod
    def strip_required_string(cls, value: object) -> object:
        """
        Remove leading and trailing spaces from required string fields.
        """
        if isinstance(value, str):
            return value.strip()

        return value

    @field_validator(
        "required_skills",
        "preferred_skills",
        "responsibilities",
        "tags",
        mode="before",
    )
    @classmethod
    def clean_string_list(cls, value: object) -> object:
        """
        Strip whitespace from list items and remove empty strings.

        Non-string values are not silently fixed. They are returned unchanged
        so Pydantic can raise a validation error.
        """
        if value is None:
            return []

        if not isinstance(value, list):
            return value

        cleaned_items = []

        for item in value:
            if not isinstance(item, str):
                return value

            cleaned_item = item.strip()

            if cleaned_item:
                cleaned_items.append(cleaned_item)

        return cleaned_items

    def to_repo2_dict(self) -> dict:
        """
        Return a JSON-compatible dictionary that can be exported to jobs.json.
        """
        return self.model_dump(mode="json")