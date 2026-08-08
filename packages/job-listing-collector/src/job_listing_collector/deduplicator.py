from __future__ import annotations

import re

from job_listing_collector.models import NormalizedJob


def deduplicate_jobs(jobs: list[NormalizedJob]) -> list[NormalizedJob]:
    """
    Remove duplicate normalized jobs while preserving first occurrence.

    Deduplication uses source_url first because it is the strongest traceable
    source identity. If source_url is missing or unusable, it falls back to
    title + company + location.
    """
    seen_keys: set[str] = set()
    unique_jobs: list[NormalizedJob] = []

    for job in jobs:
        key = build_deduplication_key(job)

        if key in seen_keys:
            continue

        seen_keys.add(key)
        unique_jobs.append(job)

    return unique_jobs


def build_deduplication_key(job: NormalizedJob) -> str:
    """
    Build a stable deduplication key for a normalized job.
    """
    source_url_key = normalize_key_part(job.source_url)

    if source_url_key:
        return f"url:{source_url_key}"

    title = normalize_key_part(job.title)
    company = normalize_key_part(job.company)
    location = normalize_key_part(job.location)

    return f"job:{title}|{company}|{location}"


def normalize_key_part(value: str) -> str:
    """
    Normalize text for deduplication comparison.

    This makes comparison less sensitive to capitalization, whitespace,
    punctuation, and trailing slashes in URLs.
    """
    normalized_value = value.strip().lower()
    normalized_value = normalized_value.rstrip("/")
    normalized_value = re.sub(r"\s+", " ", normalized_value)
    normalized_value = re.sub(r"[^a-z0-9:/._?=&%-]+", " ", normalized_value)
    normalized_value = re.sub(r"\s+", " ", normalized_value)

    return normalized_value.strip()