from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any

from preference_aware_job_recommender.data_loader import (
    load_career_profile,
    load_jobs,
)
from preference_aware_job_recommender.exporter import (
    export_recommendations_to_json,
)
from preference_aware_job_recommender.llm_scorer import (
    DEFAULT_LLM_MODEL,
    SUPPORTED_OUTPUT_LANGUAGES,
)
from preference_aware_job_recommender.recommender import recommend_jobs


DEFAULT_PROFILE_PATH = Path("examples/career_profile.json")
DEFAULT_JOBS_PATH = Path("examples/jobs.json")
DEFAULT_SCORER = "llm"


def build_parser() -> argparse.ArgumentParser:
    """
    Build the command line argument parser.
    """
    parser = argparse.ArgumentParser(
        description="Rank jobs against a structured career profile."
    )

    parser.add_argument(
        "--profile",
        default=str(DEFAULT_PROFILE_PATH),
        help="Path to the career profile JSON file.",
    )
    parser.add_argument(
        "--jobs",
        default=str(DEFAULT_JOBS_PATH),
        help="Path to the jobs JSON file.",
    )
    parser.add_argument(
        "--max-results",
        type=int,
        default=None,
        help="Maximum number of recommendations to show.",
    )
    parser.add_argument(
        "--exclude-rejected",
        action="store_true",
        help="Hide jobs rejected by hard constraints.",
    )
    parser.add_argument(
        "--output",
        default=None,
        help="Optional path for exporting recommendation results as JSON.",
    )
    parser.add_argument(
        "--scorer",
        choices=["rules", "llm"],
        default=DEFAULT_SCORER,
        help="Scoring method to use. Defaults to llm.",
    )
    parser.add_argument(
        "--llm-model",
        default=DEFAULT_LLM_MODEL,
        help="OpenAI model to use when --scorer llm is selected.",
    )
    parser.add_argument(
        "--output-language",
        choices=SUPPORTED_OUTPUT_LANGUAGES,
        default="en",
        help=(
            "Language for AI-generated recommendation explanations. "
            "Supported values: en, zh-CN. Defaults to en."
        ),
    )

    return parser


def format_recommendations(result: dict[str, Any]) -> str:
    """
    Format recommendation results for terminal output.
    """
    lines = [
        "Preference-Aware Job Recommendations",
        "=" * 42,
        f"Scoring method: {result.get('scoring_method', 'unknown')}",
        f"Total jobs scored: {result.get('total_jobs_scored', 0)}",
        (
            "Recommendations returned: "
            f"{result.get('total_recommendations_returned', 0)}"
        ),
        "",
    ]

    recommendations = result.get("recommendations", [])

    if not recommendations:
        lines.append("No recommendations found.")
        return "\n".join(lines)

    for index, recommendation in enumerate(recommendations, start=1):
        title = recommendation.get("title", "")
        company = recommendation.get("company", "")
        match_score = recommendation.get("match_score", 0)
        recommendation_level = recommendation.get("recommendation_level", "")
        missing_skills = recommendation.get("missing_skills", [])
        reasons = recommendation.get("reasons", [])
        penalties = recommendation.get("penalties", [])
        uncertainties = recommendation.get("uncertainties", [])
        is_rejected = recommendation.get("is_rejected_by_constraints", False)
        scoring_method = recommendation.get("scoring_method", "")

        lines.append(f"{index}. {title} — {company}")
        lines.append(f"   Score: {match_score} ({recommendation_level})")
        lines.append(f"   Scoring method: {scoring_method}")
        lines.append(f"   Rejected by constraints: {'yes' if is_rejected else 'no'}")

        if reasons:
            lines.append("   Reasons:")
            for reason in reasons:
                lines.append(f"   - {reason}")

        if missing_skills:
            lines.append("   Missing skills: " + ", ".join(missing_skills))

        if penalties:
            lines.append("   Penalties:")
            for penalty in penalties:
                lines.append(f"   - {penalty}")

        if uncertainties:
            lines.append("   Uncertainties:")
            for uncertainty in uncertainties:
                lines.append(f"   - {uncertainty}")

        lines.append("")

    return "\n".join(lines).rstrip()


def _print_error(message: str) -> None:
    """
    Print a user-friendly CLI error message.
    """
    print(f"Error: {message}", file=sys.stderr)


def main(argv: list[str] | None = None) -> int:
    """
    Run the command line interface.
    """
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        profile = load_career_profile(args.profile)
        jobs = load_jobs(args.jobs)

        result = recommend_jobs(
            profile=profile,
            jobs=jobs,
            max_results=args.max_results,
            include_rejected=not args.exclude_rejected,
            scorer=args.scorer,
            llm_model=args.llm_model,
            output_language=args.output_language,
        )

        print(format_recommendations(result))

        if args.output:
            output_path = export_recommendations_to_json(
                result=result,
                output_path=args.output,
            )
            print(f"\nJSON output written to: {output_path}")

        return 0

    except FileNotFoundError as error:
        missing_path = error.filename or "unknown file"
        _print_error(f"file not found: {missing_path}")
        return 1

    except PermissionError as error:
        blocked_path = error.filename or "unknown file"
        _print_error(f"permission denied: {blocked_path}")
        return 1

    except ValueError as error:
        _print_error(str(error))
        return 1

    except RuntimeError as error:
        _print_error(str(error))
        return 1

    except OSError as error:
        _print_error(str(error))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())