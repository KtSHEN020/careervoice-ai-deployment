"""Source adapters for collecting raw job listings."""

from job_listing_collector.sources.adzuna import AdzunaSource
from job_listing_collector.sources.base import (
    JobSource,
    RawJobRecord,
    SourceError,
    SourceRequest,
)

__all__ = [
    "AdzunaSource",
    "JobSource",
    "RawJobRecord",
    "SourceError",
    "SourceRequest",
]