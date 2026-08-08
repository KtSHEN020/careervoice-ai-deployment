from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator


class SourceError(RuntimeError):
    """Raised when a job source cannot collect job records."""


class SourceRequest(BaseModel):
    """
    Search request passed to a job listing source adapter.

    For example, an Adzuna source may use:

    query="junior developer"
    location="Adelaide"
    max_results=10
    """

    model_config = ConfigDict(extra="forbid")

    query: str = Field(min_length=1)
    location: str | None = None
    max_results: int = Field(default=10, ge=1, le=100)

    @field_validator("query", mode="before")
    @classmethod
    def strip_query(cls, value: object) -> object:
        if isinstance(value, str):
            return value.strip()

        return value

    @field_validator("location", mode="before")
    @classmethod
    def strip_optional_location(cls, value: object) -> object:
        if value is None:
            return None

        if isinstance(value, str):
            stripped_value = value.strip()
            return stripped_value or None

        return value


class RawJobRecord(BaseModel):
    """
    Raw job listing collected from a source adapter.

    This is not the final Repo 2-compatible schema yet.
    It is a source-independent raw record that still needs parsing and
    normalization.
    """

    model_config = ConfigDict(extra="forbid")

    source: str = Field(min_length=1)
    source_job_id: str = Field(min_length=1)
    title: str = Field(min_length=1)
    company: str = Field(min_length=1)
    location: str = Field(min_length=1)
    description: str = Field(min_length=1)
    source_url: str = Field(min_length=1)
    raw_data: dict[str, Any] = Field(default_factory=dict)

    @field_validator(
        "source",
        "source_job_id",
        "title",
        "company",
        "location",
        "description",
        "source_url",
        mode="before",
    )
    @classmethod
    def strip_required_string(cls, value: object) -> object:
        if isinstance(value, str):
            return value.strip()

        return value


class JobSource(ABC):
    """
    Base interface for all supported job listing sources.

    Each source adapter should collect raw job records from one explicitly
    supported source, such as an official API or a permitted feed.
    """

    source_name: str

    @abstractmethod
    def collect(self, request: SourceRequest) -> list[RawJobRecord]:
        """
        Collect raw job records from the source.
        """