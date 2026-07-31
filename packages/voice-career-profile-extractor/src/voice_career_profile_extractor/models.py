from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass(slots=True)
class CareerProfile:
    """
    Structured career profile extracted from user input.
    """

    target_roles: list[str] = field(default_factory=list)
    skills: list[str] = field(default_factory=list)
    experience_level: str | None = None
    preferred_locations: list[str] = field(default_factory=list)
    preferred_work_types: list[str] = field(default_factory=list)
    liked_areas: list[str] = field(default_factory=list)
    disliked_areas: list[str] = field(default_factory=list)
    hard_constraints: list[str] = field(default_factory=list)
    career_goals: list[str] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Convert the career profile into a dictionary for JSON output."""
        return asdict(self)
