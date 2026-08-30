from __future__ import annotations

from typing import Any


STOP_WORDS = {
    "a",
    "an",
    "and",
    "are",
    "as",
    "for",
    "in",
    "of",
    "or",
    "the",
    "to",
    "toward",
    "towards",
    "with",
    "move",
}


SUPPORTED_OUTPUT_LANGUAGES = (
    "en",
    "zh-CN",
)

RULE_EXPLANATION_TEMPLATES = {
    "en": {
        "matched_skills": "Matches skills: {value}",
        "matched_target_role": "Matches target role: {value}",
        "matched_experience": "Matches experience level: {value}",
        "matched_location": "Matches preferred location: {value}",
        "matched_work_type": "Matches preferred work type: {value}",
        "matched_liked_area": "Matches liked area: {value}",
        "matched_career_goal": "Supports career goal: {value}",
        "disliked_area": "Contains disliked area: {value}",
        "hard_constraint": "Conflicts with hard constraint: {value}",
    },
    "zh-CN": {
        "matched_skills": "匹配技能：{value}",
        "matched_target_role": "匹配目标岗位：{value}",
        "matched_experience": "匹配经验水平：{value}",
        "matched_location": "匹配偏好地区：{value}",
        "matched_work_type": "匹配偏好工作方式：{value}",
        "matched_liked_area": "匹配感兴趣领域：{value}",
        "matched_career_goal": "支持职业目标：{value}",
        "disliked_area": "包含不喜欢的领域：{value}",
        "hard_constraint": "与不可妥协要求冲突：{value}",
    },
}


def _normalize_output_language(
    output_language: str,
) -> str:
    """Validate the requested rule-based explanation language."""
    if not isinstance(
        output_language,
        str,
    ):
        raise ValueError(
            "output_language must be one of: en, zh-CN."
        )

    cleaned_language = (
        output_language.strip()
    )

    if (
        cleaned_language
        not in SUPPORTED_OUTPUT_LANGUAGES
    ):
        raise ValueError(
            "output_language must be one of: en, zh-CN."
        )

    return cleaned_language


def normalize_text(value: str) -> str:
    """
    Normalize text for simple case-insensitive matching.
    """
    return " ".join(value.lower().strip().split())


def _as_string_list(value: Any) -> list[str]:
    """
    Return a list only if the input is a list of strings.
    """
    if not isinstance(value, list):
        return []

    return [item for item in value if isinstance(item, str)]


def _find_matched_items(user_items: list[str], target_items: list[str]) -> list[str]:
    """
    Find target items that appear in the user's items.
    """
    normalized_user_items = {normalize_text(item) for item in user_items}

    return [
        item
        for item in target_items
        if normalize_text(item) in normalized_user_items
    ]


def _find_missing_items(user_items: list[str], target_items: list[str]) -> list[str]:
    """
    Find target items that do not appear in the user's items.
    """
    normalized_user_items = {normalize_text(item) for item in user_items}

    return [
        item
        for item in target_items
        if normalize_text(item) not in normalized_user_items
    ]


def _build_job_search_text(job: dict[str, Any]) -> str:
    """
    Build a searchable text string from job fields.
    """
    text_parts = [
        str(job.get("title", "")),
        str(job.get("company", "")),
        str(job.get("location", "")),
        str(job.get("work_type", "")),
        str(job.get("seniority", "")),
        str(job.get("description", "")),
    ]

    list_fields = [
        "required_skills",
        "preferred_skills",
        "responsibilities",
        "tags",
    ]

    for field in list_fields:
        text_parts.extend(_as_string_list(job.get(field, [])))

    return normalize_text(" ".join(text_parts))


def _find_text_matches(preferences: list[str], searchable_text: str) -> list[str]:
    """
    Find preference phrases that appear in the job search text.
    """
    return [
        preference
        for preference in preferences
        if normalize_text(preference) in searchable_text
    ]


def _tokenize_meaningful_words(text: str) -> set[str]:
    """
    Convert text into meaningful words for simple goal matching.
    """
    words = normalize_text(text).replace("-", " ").split()

    return {
        word
        for word in words
        if word not in STOP_WORDS and len(word) > 1
    }


def _find_career_goal_matches(
    career_goals: list[str],
    searchable_text: str,
) -> list[str]:
    """
    Find career goals that share meaningful words with the job text.
    """
    job_words = _tokenize_meaningful_words(searchable_text)
    matched_goals = []

    for goal in career_goals:
        goal_words = _tokenize_meaningful_words(goal)

        if goal_words.intersection(job_words):
            matched_goals.append(goal)

    return matched_goals


def _has_exact_match(options: list[str], value: str) -> bool:
    """
    Check whether a value exactly matches one of the options.
    """
    normalized_value = normalize_text(value)

    if not normalized_value:
        return False

    normalized_options = {
        normalize_text(option)
        for option in options
        if normalize_text(option)
    }

    return normalized_value in normalized_options


def _extract_constraint_target(constraint: str) -> str:
    """
    Extract the main target phrase from a simple hard constraint.
    """
    normalized_constraint = normalize_text(constraint)

    removable_words = [
        "avoid",
        "roles",
        "role",
        "jobs",
        "job",
    ]

    words = [
        word
        for word in normalized_constraint.split()
        if word not in removable_words
    ]

    return " ".join(words)


def _find_hard_constraint_conflicts(
    hard_constraints: list[str],
    searchable_text: str,
) -> list[str]:
    """
    Find hard constraints that conflict with a job.
    """
    conflicts = []

    for constraint in hard_constraints:
        target = _extract_constraint_target(constraint)

        if target and target in searchable_text:
            conflicts.append(constraint)

    return conflicts


def calculate_skill_match(profile: dict[str, Any], job: dict[str, Any]) -> dict[str, Any]:
    """
    Calculate skill match details between a career profile and a job.
    """
    profile_skills = _as_string_list(profile.get("skills", []))
    required_skills = _as_string_list(job.get("required_skills", []))
    preferred_skills = _as_string_list(job.get("preferred_skills", []))

    matched_required_skills = _find_matched_items(profile_skills, required_skills)
    matched_preferred_skills = _find_matched_items(profile_skills, preferred_skills)

    missing_required_skills = _find_missing_items(profile_skills, required_skills)
    missing_preferred_skills = _find_missing_items(profile_skills, preferred_skills)

    required_skill_weight = 2
    preferred_skill_weight = 1

    total_possible_points = (
        len(required_skills) * required_skill_weight
        + len(preferred_skills) * preferred_skill_weight
    )

    matched_points = (
        len(matched_required_skills) * required_skill_weight
        + len(matched_preferred_skills) * preferred_skill_weight
    )

    if total_possible_points == 0:
        skill_match_score = 0
    else:
        skill_match_score = int((matched_points / total_possible_points) * 100 + 0.5)

    return {
        "skill_match_score": skill_match_score,
        "matched_required_skills": matched_required_skills,
        "matched_preferred_skills": matched_preferred_skills,
        "matched_skills": matched_required_skills + matched_preferred_skills,
        "missing_required_skills": missing_required_skills,
        "missing_preferred_skills": missing_preferred_skills,
        "missing_skills": missing_required_skills + missing_preferred_skills,
    }


def get_recommendation_level(match_score: int) -> str:
    """
    Convert a numeric match score into a recommendation level.
    """
    if match_score >= 80:
        return "strong_match"

    if match_score >= 60:
        return "good_match"

    if match_score >= 40:
        return "partial_match"

    return "poor_match"


def _build_positive_reasons(
    skill_result: dict[str, Any],
    matched_target_roles: list[str],
    experience_matches: bool,
    job_seniority: str,
    location_matches: bool,
    job_location: str,
    work_type_matches: bool,
    job_work_type: str,
    matched_liked_areas: list[str],
    matched_career_goals: list[str],
    *,
    output_language: str,
) -> list[str]:
    """
    Build localized explanation reasons for positive matching factors.
    """
    templates = (
        RULE_EXPLANATION_TEMPLATES[
            output_language
        ]
    )

    reasons = []

    if skill_result["matched_skills"]:
        reasons.append(
            templates[
                "matched_skills"
            ].format(
                value=", ".join(
                    skill_result[
                        "matched_skills"
                    ]
                )
            )
        )

    if matched_target_roles:
        reasons.append(
            templates[
                "matched_target_role"
            ].format(
                value=(
                    matched_target_roles[0]
                )
            )
        )

    if experience_matches:
        reasons.append(
            templates[
                "matched_experience"
            ].format(
                value=job_seniority
            )
        )

    if location_matches:
        reasons.append(
            templates[
                "matched_location"
            ].format(
                value=job_location
            )
        )

    if work_type_matches:
        reasons.append(
            templates[
                "matched_work_type"
            ].format(
                value=job_work_type
            )
        )

    if matched_liked_areas:
        reasons.append(
            templates[
                "matched_liked_area"
            ].format(
                value=(
                    matched_liked_areas[0]
                )
            )
        )

    if matched_career_goals:
        reasons.append(
            templates[
                "matched_career_goal"
            ].format(
                value=(
                    matched_career_goals[0]
                )
            )
        )

    return reasons


def _build_penalties(
    matched_disliked_areas: list[str],
    hard_constraint_conflicts: list[str],
    *,
    output_language: str,
) -> list[str]:
    """
    Build localized explanation messages for penalties.
    """
    templates = (
        RULE_EXPLANATION_TEMPLATES[
            output_language
        ]
    )

    penalties = []

    for disliked_area in (
        matched_disliked_areas
    ):
        penalties.append(
            templates[
                "disliked_area"
            ].format(
                value=disliked_area
            )
        )

    for conflict in (
        hard_constraint_conflicts
    ):
        penalties.append(
            templates[
                "hard_constraint"
            ].format(
                value=conflict
            )
        )

    return penalties


def score_job(
    profile: dict[str, Any],
    job: dict[str, Any],
    *,
    output_language: str = "en",
) -> dict[str, Any]:
    """
    Score a job against a career profile using positive and negative factors.
    """
    normalized_output_language = (
        _normalize_output_language(
            output_language
        )
    )
    skill_result = calculate_skill_match(profile, job)
    searchable_text = _build_job_search_text(job)

    target_roles = _as_string_list(profile.get("target_roles", []))
    preferred_locations = _as_string_list(profile.get("preferred_locations", []))
    preferred_work_types = _as_string_list(profile.get("preferred_work_types", []))
    liked_areas = _as_string_list(profile.get("liked_areas", []))
    disliked_areas = _as_string_list(profile.get("disliked_areas", []))
    hard_constraints = _as_string_list(profile.get("hard_constraints", []))
    career_goals = _as_string_list(profile.get("career_goals", []))

    job_location = str(job.get("location", ""))
    job_work_type = str(job.get("work_type", ""))
    job_seniority = str(job.get("seniority", ""))
    profile_experience_level = str(profile.get("experience_level", ""))

    matched_target_roles = _find_text_matches(target_roles, searchable_text)
    matched_liked_areas = _find_text_matches(liked_areas, searchable_text)
    matched_disliked_areas = _find_text_matches(disliked_areas, searchable_text)
    matched_career_goals = _find_career_goal_matches(career_goals, searchable_text)
    hard_constraint_conflicts = _find_hard_constraint_conflicts(
        hard_constraints,
        searchable_text,
    )

    experience_matches = bool(profile_experience_level and job_seniority) and (
        normalize_text(profile_experience_level) == normalize_text(job_seniority)
        )
    location_matches = _has_exact_match(preferred_locations, job_location)
    work_type_matches = _has_exact_match(preferred_work_types, job_work_type)

    skill_score = int(skill_result["skill_match_score"] * 0.4 + 0.5)
    target_role_score = 20 if matched_target_roles else 0
    experience_score = 10 if experience_matches else 0
    location_score = 10 if location_matches else 0
    work_type_score = 10 if work_type_matches else 0
    liked_area_score = 5 if matched_liked_areas else 0
    career_goal_score = 5 if matched_career_goals else 0

    positive_score = (
        skill_score
        + target_role_score
        + experience_score
        + location_score
        + work_type_score
        + liked_area_score
        + career_goal_score
    )

    dislike_penalty = min(len(matched_disliked_areas) * 15, 30)
    hard_constraint_penalty = min(len(hard_constraint_conflicts) * 40, 80)
    total_penalty = dislike_penalty + hard_constraint_penalty

    match_score = max(0, positive_score - total_penalty)

    if hard_constraint_conflicts:
        match_score = min(match_score, 25)

    reasons = _build_positive_reasons(
        skill_result=skill_result,
        matched_target_roles=matched_target_roles,
        experience_matches=experience_matches,
        job_seniority=job_seniority,
        location_matches=location_matches,
        job_location=job_location,
        work_type_matches=work_type_matches,
        job_work_type=job_work_type,
        matched_liked_areas=matched_liked_areas,
        matched_career_goals=matched_career_goals,
        output_language=(
            normalized_output_language
        ),
    )
    penalties = _build_penalties(
        matched_disliked_areas=(
            matched_disliked_areas
        ),
        hard_constraint_conflicts=(
            hard_constraint_conflicts
        ),
        output_language=(
            normalized_output_language
        ),
    )

    return {
        "job_id": job.get("job_id", ""),
        "title": job.get("title", ""),
        "company": job.get("company", ""),
        "match_score": match_score,
        "recommendation_level": get_recommendation_level(match_score),
        "reasons": reasons,
        "missing_skills": skill_result["missing_skills"],
        "penalties": penalties,
        "is_rejected_by_constraints": bool(hard_constraint_conflicts),
        "score_breakdown": {
            "positive_score": positive_score,
            "total_penalty": total_penalty,
            "skill_match": skill_score,
            "target_role_match": target_role_score,
            "experience_match": experience_score,
            "location_match": location_score,
            "work_type_match": work_type_score,
            "liked_area_match": liked_area_score,
            "career_goal_match": career_goal_score,
            "dislike_penalty": dislike_penalty,
            "hard_constraint_penalty": hard_constraint_penalty,
        },
        "matched_details": {
            "matched_target_roles": matched_target_roles,
            "matched_liked_areas": matched_liked_areas,
            "matched_disliked_areas": matched_disliked_areas,
            "matched_career_goals": matched_career_goals,
            "matched_hard_constraints": hard_constraint_conflicts,
            "matched_skills": skill_result["matched_skills"],
        },
    }