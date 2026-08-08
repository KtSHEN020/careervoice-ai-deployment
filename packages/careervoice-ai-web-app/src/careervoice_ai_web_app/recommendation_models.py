from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass

SUPPORTED_RECOMMENDATION_SCORERS = (
    "rules",
    "llm",
)

MIN_RECOMMENDATIONS = 1
MAX_RECOMMENDATIONS = 50

RECOMMENDATION_LIST_FIELDS = (
    "reasons",
    "missing_skills",
    "penalties",
    "uncertainties",
)


def _validate_nonnegative_integer(
    value: object,
    *,
    field_name: str,
) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise ValueError(
            f"Recommendation field '{field_name}' must be a whole number."
        )

    if value < 0:
        raise ValueError(
            f"Recommendation field '{field_name}' cannot be negative."
        )

    return value


def _validate_string_list(
    value: object,
    *,
    field_name: str,
) -> list[str]:
    if not isinstance(value, list):
        raise ValueError(
            f"Recommendation field '{field_name}' must be a list of strings."
        )

    if not all(isinstance(item, str) for item in value):
        raise ValueError(
            f"Recommendation field '{field_name}' must contain only strings."
        )

    return list(value)


def _validate_recommendation(
    value: object,
    *,
    index: int,
) -> dict[str, object]:
    if not isinstance(value, dict):
        raise ValueError(
            "Recommendation results must contain only JSON objects. "
            f"Invalid item at index {index}."
        )

    recommendation = dict(value)

    match_score = recommendation.get("match_score")

    if (
        isinstance(match_score, bool)
        or not isinstance(match_score, int)
        or not 0 <= match_score <= 100
    ):
        raise ValueError(
            "Recommendation field 'match_score' must be a whole number "
            "between 0 and 100."
        )

    rejected = recommendation.get("is_rejected_by_constraints")

    if not isinstance(rejected, bool):
        raise ValueError(
            "Recommendation field 'is_rejected_by_constraints' "
            "must be true or false."
        )

    for field_name in (
        "job_id",
        "title",
        "company",
        "recommendation_level",
        "scoring_method",
    ):
        if (
            field_name in recommendation
            and not isinstance(recommendation[field_name], str)
        ):
            raise ValueError(
                f"Recommendation field '{field_name}' must be text."
            )

    for field_name in RECOMMENDATION_LIST_FIELDS:
        if field_name not in recommendation:
            continue

        recommendation[field_name] = _validate_string_list(
            recommendation[field_name],
            field_name=field_name,
        )

    for field_name in (
        "score_breakdown",
        "matched_details",
    ):
        if (
            field_name in recommendation
            and not isinstance(recommendation[field_name], Mapping)
        ):
            raise ValueError(
                f"Recommendation field '{field_name}' must be an object."
            )

    return recommendation


@dataclass(frozen=True)
class RecommendationSettings:
    """Validated settings for one recommendation run."""

    scorer: str
    max_results: int
    exclude_rejected: bool

    @classmethod
    def from_values(
        cls,
        *,
        scorer: object,
        max_results: object,
        exclude_rejected: object,
    ) -> RecommendationSettings:
        """Create validated recommendation settings from user input."""
        if not isinstance(scorer, str):
            raise ValueError("Ranking method must be text.")

        normalized_scorer = scorer.strip().lower()

        if normalized_scorer not in SUPPORTED_RECOMMENDATION_SCORERS:
            raise ValueError(
                "Unsupported ranking method. Choose 'rules' or 'llm'."
            )

        if isinstance(max_results, bool) or not isinstance(max_results, int):
            raise ValueError(
                "Maximum recommendations must be a whole number."
            )

        if not MIN_RECOMMENDATIONS <= max_results <= MAX_RECOMMENDATIONS:
            raise ValueError(
                "Maximum recommendations must be between "
                f"{MIN_RECOMMENDATIONS} and {MAX_RECOMMENDATIONS}."
            )

        if not isinstance(exclude_rejected, bool):
            raise ValueError(
                "The rejected-job setting must be true or false."
            )

        return cls(
            scorer=normalized_scorer,
            max_results=max_results,
            exclude_rejected=exclude_rejected,
        )

    def to_state_dict(self) -> dict[str, object]:
        """Return settings suitable for Streamlit session state."""
        return {
            "scorer": self.scorer,
            "max_results": self.max_results,
            "exclude_rejected": self.exclude_rejected,
        }


@dataclass(frozen=True)
class RecommendationDocument:
    """Validated recommendation output returned by the ranking stage."""

    document: dict[str, object]
    recommendations: tuple[dict[str, object], ...]
    total_jobs_scored: int
    total_recommendations_returned: int
    scoring_method: str

    @classmethod
    def from_mapping(
        cls,
        value: Mapping[str, object],
    ) -> RecommendationDocument:
        """Validate and normalize a recommendation document."""
        document = dict(value)

        raw_recommendations = document.get("recommendations")

        if not isinstance(raw_recommendations, list):
            raise ValueError(
                "Recommendation output must contain a "
                "'recommendations' list."
            )

        recommendations = tuple(
            _validate_recommendation(
                recommendation,
                index=index,
            )
            for index, recommendation in enumerate(raw_recommendations)
        )

        total_jobs_scored = _validate_nonnegative_integer(
            document.get("total_jobs_scored"),
            field_name="total_jobs_scored",
        )

        total_returned = _validate_nonnegative_integer(
            document.get("total_recommendations_returned"),
            field_name="total_recommendations_returned",
        )

        if total_returned != len(recommendations):
            raise ValueError(
                "The reported recommendation count does not match "
                "the recommendation list."
            )

        scoring_method = document.get("scoring_method")

        if not isinstance(scoring_method, str):
            raise ValueError(
                "Recommendation field 'scoring_method' must be text."
            )

        normalized_scoring_method = scoring_method.strip().lower()

        if normalized_scoring_method not in SUPPORTED_RECOMMENDATION_SCORERS:
            raise ValueError(
                "Recommendation output contains an unsupported "
                "scoring method."
            )

        document["recommendations"] = [
            dict(recommendation)
            for recommendation in recommendations
        ]
        document["scoring_method"] = normalized_scoring_method

        return cls(
            document=document,
            recommendations=recommendations,
            total_jobs_scored=total_jobs_scored,
            total_recommendations_returned=total_returned,
            scoring_method=normalized_scoring_method,
        )