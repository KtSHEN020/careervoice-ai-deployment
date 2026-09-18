import re

from voice_career_profile_extractor.models import CareerProfile

SKILL_KEYWORDS = {
    "python": "Python",
    "sql": "SQL",
    "git": "Git",
    "react": "React",
    "javascript": "JavaScript",
    "typescript": "TypeScript",
    "html": "HTML",
    "css": "CSS",
    "machine learning": "machine learning",
    "data analysis": "data analysis",
    "pandas": "pandas",
    "numpy": "NumPy",
    "scikit-learn": "scikit-learn",
    "docker": "Docker",
    "linux": "Linux",
}

TARGET_ROLE_KEYWORDS = {
    "junior software developer": "junior software developer",
    "software developer": "software developer",
    "backend developer": "backend developer",
    "back-end developer": "backend developer",
    "backend": "backend developer",
    "data analyst": "data analyst",
    "data-related": "data analyst",
    "data related": "data analyst",
    "software engineer": "software engineer",
    "ai engineer": "AI engineer",
    "machine learning engineer": "machine learning engineer",
}

LOCATION_KEYWORDS = {
    "adelaide": "Adelaide",
    "sydney": "Sydney",
    "melbourne": "Melbourne",
    "brisbane": "Brisbane",
    "perth": "Perth",
    "canberra": "Canberra",
    "remote": "remote",
    "australia": "Australia",
}

WORK_TYPE_KEYWORDS = {
    "remote": "remote",
    "hybrid": "hybrid",
    "on-site": "on-site",
    "onsite": "on-site",
    "full-time": "full-time",
    "full time": "full-time",
    "part-time": "part-time",
    "part time": "part-time",
    "contract": "contract",
    "internship": "internship",
}

LIKED_AREA_KEYWORDS = {
    "backend": "backend development",
    "back-end": "backend development",
    "data-related": "data-related roles",
    "data related": "data-related roles",
    "data": "data-related roles",
    "ai": "AI tools",
    "artificial intelligence": "AI tools",
    "software engineering": "software engineering",
}

DISLIKED_AREA_KEYWORDS = {
    "sales": "sales",
    "customer service": "customer service",
    "senior role": "senior roles",
    "senior roles": "senior roles",
    "management": "management",
    "cold calling": "cold calling",
}

POSITIVE_PREFERENCE_PATTERN = re.compile(
    r"(?:"
    r"\bi\s+(?:like|love|enjoy|prefer)\s+"
    r"|"
    r"\b(?:i am|i'm)\s+interested\s+in\s+"
    r")"
    r"(?!not\b)"
    r"(.+?)"
    r"(?="
    r"\s+(?:but|however|although|though)\b"
    r"|,\s*not\b"
    r"|$"
    r")",
    re.IGNORECASE,
)

NEGATIVE_PATTERN = re.compile(
    r"(?:do not want|don't want|do not like|don't like|avoid|not interested in)"
    r"\s+(.+?)(?:[.!?]|$)",
    re.IGNORECASE,
)

GOAL_PATTERN = re.compile(
    r"(?:goal is to|goal is|goal:)\s+(.+)",
    re.IGNORECASE,
)


def extract_career_profile(text: str) -> CareerProfile:
    """Extract a structured career profile from transcript or text input."""
    normalized_text = _normalize_text(text)

    profile = CareerProfile()
    profile.target_roles = _extract_target_roles(normalized_text)
    profile.skills = _extract_keyword_values(normalized_text, SKILL_KEYWORDS)
    profile.experience_level = _extract_experience_level(normalized_text)
    profile.preferred_locations = _extract_keyword_values(
        normalized_text,
        LOCATION_KEYWORDS,
    )
    profile.preferred_work_types = _extract_keyword_values(
        normalized_text,
        WORK_TYPE_KEYWORDS,
    )
    profile.liked_areas = _extract_liked_areas(
        normalized_text,
    )
    profile.disliked_areas = _extract_disliked_areas(normalized_text)
    profile.hard_constraints = _build_hard_constraints(profile.disliked_areas)
    profile.career_goals = _extract_career_goals(text)
    profile.notes = _build_notes(profile)

    return profile


def _normalize_text(text: str) -> str:
    return " ".join(text.lower().split())


def _contains_phrase(normalized_text: str, phrase: str) -> bool:
    pattern = rf"(?<!\w){re.escape(phrase)}(?!\w)"
    return re.search(pattern, normalized_text) is not None


def _extract_keyword_values(
    normalized_text: str,
    keyword_map: dict[str, str],
) -> list[str]:
    values = [
        value
        for keyword, value in keyword_map.items()
        if _contains_phrase(normalized_text, keyword)
    ]

    return _deduplicate(values)


def _extract_target_roles(normalized_text: str) -> list[str]:
    roles = _extract_keyword_values(normalized_text, TARGET_ROLE_KEYWORDS)

    if "junior software developer" in roles and "software developer" in roles:
        roles.remove("software developer")

    return roles


def _extract_experience_level(normalized_text: str) -> str | None:
    junior_keywords = ["junior", "entry-level", "entry level", "graduate"]
    mid_level_keywords = ["mid-level", "mid level"]
    senior_keywords = ["senior", "lead", "principal"]

    if any(_contains_phrase(normalized_text, keyword) for keyword in junior_keywords):
        return "junior"

    if any(
        _contains_phrase(normalized_text, keyword) for keyword in mid_level_keywords
    ):
        return "mid-level"

    negative_segments = " ".join(_extract_negative_segments(normalized_text))
    has_senior_keyword = any(
        _contains_phrase(normalized_text, keyword) for keyword in senior_keywords
    )

    if has_senior_keyword and "senior" not in negative_segments:
        return "senior"

    return None


def _extract_negative_segments(normalized_text: str) -> list[str]:
    return [
        match.group(1).strip() for match in NEGATIVE_PATTERN.finditer(normalized_text)
    ]


def _extract_liked_areas(
    normalized_text: str,
) -> list[str]:
    liked_areas = []

    for sentence in _split_sentences(
        normalized_text
    ):
        for match in (
            POSITIVE_PREFERENCE_PATTERN.finditer(
                sentence
            )
        ):
            preference_segment = (
                match.group(1).strip()
            )

            liked_areas.extend(
                _extract_keyword_values(
                    preference_segment,
                    LIKED_AREA_KEYWORDS,
                )
            )

    return _deduplicate(liked_areas)


def _extract_disliked_areas(normalized_text: str) -> list[str]:
    negative_segments = _extract_negative_segments(normalized_text)
    disliked_areas = []

    for segment in negative_segments:
        disliked_areas.extend(_extract_keyword_values(segment, DISLIKED_AREA_KEYWORDS))

    return _deduplicate(disliked_areas)


def _build_hard_constraints(disliked_areas: list[str]) -> list[str]:
    constraints = []

    for area in disliked_areas:
        if area.endswith("roles"):
            constraints.append(f"avoid {area}")
        else:
            constraints.append(f"avoid {area} roles")

    return constraints


def _extract_career_goals(text: str) -> list[str]:
    goals = []

    for sentence in _split_sentences(text):
        match = GOAL_PATTERN.search(sentence)

        if match:
            goals.append(_clean_extracted_text(match.group(1)))

    return _deduplicate(goals)


def _split_sentences(text: str) -> list[str]:
    return [sentence.strip() for sentence in re.split(r"(?<=[.!?])\s+", text.strip())]


def _clean_extracted_text(text: str) -> str:
    return text.strip().strip(" .!?")


def _build_notes(profile: CareerProfile) -> list[str]:
    notes = []

    if not profile.target_roles:
        notes.append("No clear target roles found.")

    if not profile.skills:
        notes.append("No clear skills found.")

    if profile.experience_level is None:
        notes.append("No clear experience level found.")

    if not profile.preferred_locations:
        notes.append("No preferred locations found.")

    return notes


def _deduplicate(values: list[str]) -> list[str]:
    deduplicated_values = []

    for value in values:
        if value not in deduplicated_values:
            deduplicated_values.append(value)

    return deduplicated_values
