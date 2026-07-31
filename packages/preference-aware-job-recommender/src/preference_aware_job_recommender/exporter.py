from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def export_recommendations_to_json(
    result: dict[str, Any],
    output_path: str | Path,
) -> Path:
    """Export recommendation results to a formatted JSON file."""
    path = Path(output_path)

    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("w", encoding="utf-8") as file:
        json.dump(result, file, indent=2, ensure_ascii=False)
        file.write("\n")

    return path