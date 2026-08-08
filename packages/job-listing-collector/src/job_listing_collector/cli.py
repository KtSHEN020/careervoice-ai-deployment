from __future__ import annotations

import argparse
import sys
from pathlib import Path

from pydantic import ValidationError

from job_listing_collector.config import create_adzuna_source
from job_listing_collector.deduplicator import deduplicate_jobs
from job_listing_collector.exporter import export_jobs
from job_listing_collector.normalizer import normalize_raw_jobs
from job_listing_collector.sources import JobSource, SourceError, SourceRequest


SUPPORTED_SOURCES = ("adzuna",)


def build_parser() -> argparse.ArgumentParser:
    """
    Build the command-line parser for the job collection pipeline.
    """
    parser = argparse.ArgumentParser(
        prog="job-collect",
        description="Collect job listings and export Repo 2-compatible jobs.json.",
    )

    parser.add_argument(
        "--source",
        choices=SUPPORTED_SOURCES,
        required=True,
        help="Job listing source to collect from.",
    )
    parser.add_argument(
        "--query",
        dest="queries",
        action="append",
        required=True,
        help=(
            "Job search query. Repeat this option to collect jobs for "
            "multiple queries."
        ),
    )
    parser.add_argument(
        "--location",
        default=None,
        help='Optional job search location, for example "Adelaide".',
    )
    parser.add_argument(
        "--max-results",
        "--max_results",
        dest="max_results",
        type=int,
        default=10,
        help="Maximum number of jobs to request for each query.",
    )
    parser.add_argument(
        "--output",
        default="outputs/jobs.json",
        help="Path to write the exported jobs.json file.",
    )
    parser.add_argument(
        "--normalizer",
        choices=("rule",),
        default="rule",
        help="Normalization mode. Only rule-based normalization is supported for now.",
    )

    return parser


def create_source(source_name: str) -> JobSource:
    """
    Create a supported source adapter by name.
    """
    if source_name == "adzuna":
        return create_adzuna_source()

    raise ValueError(f"Unsupported source: {source_name}")


def normalize_queries(queries: list[str]) -> list[str]:
    """
    Clean and deduplicate job search queries while preserving their order.

    Queries are compared case-insensitively so repeated values such as
    "Software Developer" and "software developer" only trigger one request.
    """
    unique_queries: list[str] = []
    seen_queries: set[str] = set()

    for value in queries:
        query = value.strip()

        if not query:
            raise ValueError("Job search queries cannot be empty.")

        comparison_key = query.casefold()

        if comparison_key in seen_queries:
            continue

        seen_queries.add(comparison_key)
        unique_queries.append(query)

    if not unique_queries:
        raise ValueError("At least one job search query is required.")

    return unique_queries


def run_pipeline(args: argparse.Namespace) -> Path:
    """
    Run the full collection pipeline and return the output path.

    Each query is validated and collected separately. All raw jobs are then
    normalized and deduplicated together before one combined jobs.json file
    is exported.
    """
    queries = normalize_queries(args.queries)

    requests = [
        SourceRequest(
            query=query,
            location=args.location,
            max_results=args.max_results,
        )
        for query in queries
    ]

    source = create_source(args.source)
    raw_jobs = []

    for query, request in zip(queries, requests, strict=True):
        query_jobs = source.collect(request)
        raw_jobs.extend(query_jobs)

        print(f'Query "{query}": collected {len(query_jobs)} raw jobs.')

    normalized_jobs = normalize_raw_jobs(raw_jobs)
    unique_jobs = deduplicate_jobs(normalized_jobs)
    output_path = export_jobs(unique_jobs, args.output)

    query_label = "query" if len(queries) == 1 else "queries"

    print(
        f"Collected {len(raw_jobs)} raw jobs from {args.source} "
        f"across {len(queries)} {query_label}."
    )
    print(f"Normalized {len(normalized_jobs)} jobs.")
    print(f"Exported {len(unique_jobs)} unique jobs to {output_path}.")

    return output_path


def main(argv: list[str] | None = None) -> int:
    """
    CLI entry point.

    Returns 0 on success and 1 on handled errors.
    """
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        run_pipeline(args)
    except (RuntimeError, SourceError, ValueError, ValidationError) as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())