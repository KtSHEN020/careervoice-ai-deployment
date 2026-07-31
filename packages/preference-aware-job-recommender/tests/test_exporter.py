import json
from pathlib import Path

from preference_aware_job_recommender.exporter import (
    export_recommendations_to_json,
)


def test_export_recommendations_to_json_creates_file(tmp_path: Path) -> None:
    result = {
        "recommendations": [
            {
                "job_id": "job_001",
                "title": "Junior Backend Developer",
                "match_score": 86,
            }
        ],
        "total_jobs_scored": 1,
        "total_recommendations_returned": 1,
    }

    output_path = tmp_path / "outputs" / "recommendations.json"

    returned_path = export_recommendations_to_json(
        result=result,
        output_path=output_path,
    )

    assert returned_path == output_path
    assert output_path.exists()


def test_export_recommendations_to_json_preserves_content(tmp_path: Path) -> None:
    result = {
        "recommendations": [
            {
                "job_id": "job_001",
                "title": "Junior Backend Developer",
                "match_score": 86,
            }
        ],
        "total_jobs_scored": 1,
        "total_recommendations_returned": 1,
    }

    output_path = tmp_path / "recommendations.json"

    export_recommendations_to_json(
        result=result,
        output_path=output_path,
    )

    with output_path.open(encoding="utf-8") as file:
        exported_result = json.load(file)

    assert exported_result == result