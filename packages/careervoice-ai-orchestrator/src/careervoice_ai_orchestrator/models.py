from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


SUPPORTED_INPUT_MODES = ("profile", "text", "voice")
SUPPORTED_PROFILE_EXTRACTORS = ("rules", "llm")
SUPPORTED_JOB_SOURCES = ("adzuna",)
SUPPORTED_RECOMMENDER_SCORERS = ("rules", "llm")


def normalize_job_queries(values: tuple[str, ...]) -> tuple[str, ...]:
    """
    Clean and deduplicate job queries while preserving their original order.
    """
    normalized_queries: list[str] = []
    seen_queries: set[str] = set()

    for value in values:
        if not isinstance(value, str):
            raise ValueError("job_queries must contain only strings.")

        query = value.strip()

        if not query:
            raise ValueError("job_queries cannot contain empty values.")

        comparison_key = query.casefold()

        if comparison_key in seen_queries:
            continue

        seen_queries.add(comparison_key)
        normalized_queries.append(query)

    return tuple(normalized_queries)


@dataclass(frozen=True)
class WorkflowConfig:
    """
    Configuration for one CareerVoice AI orchestration run.

    This object stores the file paths and options needed to connect
    the profile extractor, job collector, and job recommender repositories.
    """

    input_mode: str = "profile"

    profile_input_path: Path = Path("outputs/profile_input.txt")
    profile_path: Path = Path("examples/career_profile.json")
    jobs_output_path: Path = Path("outputs/jobs.json")
    recommendations_output_path: Path = Path("outputs/recommendations.json")

    profile_extractor: str = "rules"

    job_source: str = "adzuna"
    job_queries: tuple[str, ...] = ()
    job_location: str | None = "Adelaide"
    job_max_results: int = 10

    recommender_scorer: str = "rules"
    recommendation_max_results: int = 10
    exclude_rejected: bool = False

    def __post_init__(self) -> None:
        """
        Normalize path fields and validate configuration values.
        """
        object.__setattr__(self, "profile_input_path", Path(self.profile_input_path))
        object.__setattr__(self, "profile_path", Path(self.profile_path))
        object.__setattr__(self, "jobs_output_path", Path(self.jobs_output_path))
        object.__setattr__(
            self,
            "recommendations_output_path",
            Path(self.recommendations_output_path),
        )
        object.__setattr__(
            self,
            "job_queries",
            normalize_job_queries(tuple(self.job_queries)),
        )

        if self.input_mode not in SUPPORTED_INPUT_MODES:
            supported = ", ".join(SUPPORTED_INPUT_MODES)
            raise ValueError(
                f"Unsupported input mode: {self.input_mode}. "
                f"Supported input modes: {supported}."
            )

        if self.profile_extractor not in SUPPORTED_PROFILE_EXTRACTORS:
            supported = ", ".join(SUPPORTED_PROFILE_EXTRACTORS)
            raise ValueError(
                f"Unsupported profile extractor: {self.profile_extractor}. "
                f"Supported extractors: {supported}."
            )

        if self.job_source not in SUPPORTED_JOB_SOURCES:
            supported = ", ".join(SUPPORTED_JOB_SOURCES)
            raise ValueError(
                f"Unsupported job source: {self.job_source}. "
                f"Supported sources: {supported}."
            )

        if self.job_max_results < 1:
            raise ValueError("job_max_results must be at least 1.")

        if self.recommender_scorer not in SUPPORTED_RECOMMENDER_SCORERS:
            supported = ", ".join(SUPPORTED_RECOMMENDER_SCORERS)
            raise ValueError(
                f"Unsupported recommender scorer: {self.recommender_scorer}. "
                f"Supported scorers: {supported}."
            )

        if self.recommendation_max_results < 1:
            raise ValueError("recommendation_max_results must be at least 1.")

    @property
    def output_directories(self) -> tuple[Path, ...]:
        """
        Return directories that should exist before writing workflow outputs.
        """
        return (
            self.profile_input_path.parent,
            self.profile_path.parent,
            self.jobs_output_path.parent,
            self.recommendations_output_path.parent,
        )