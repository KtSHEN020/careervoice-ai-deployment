from __future__ import annotations

import json
from pathlib import Path

from job_listing_collector.models import NormalizedJob


def export_jobs(jobs: list[NormalizedJob], output_path: str | Path) -> Path:
    """
    Export normalized jobs to a JSON file.

    The output is a list of dictionaries that can be used as jobs.json input
    for the preference-aware-job-recommender repo.
    """
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    job_data = [job.to_repo2_dict() for job in jobs]

    with path.open("w", encoding="utf-8") as file:
        json.dump(job_data, file, indent=2, ensure_ascii=False)

    return path