from __future__ import annotations

import re
from datetime import datetime, timezone
from html import unescape

from job_listing_collector.models import NormalizedJob
from job_listing_collector.sources import RawJobRecord


SKILL_PATTERNS: dict[str, list[str]] = {
    "Python": [r"\bpython\b"],
    "SQL": [r"\bsql\b"],
    "Git": [r"\bgit\b"],
    "JavaScript": [r"\bjavascript\b", r"\bjs\b"],
    "TypeScript": [r"\btypescript\b", r"\bts\b"],
    "Java": [r"\bjava\b"],
    "C#": [r"\bc#\b", r"\bc sharp\b"],
    "C++": [r"\bc\+\+\b"],
    "React": [r"\breact\b", r"\breact\.js\b"],
    "Node.js": [r"\bnode\.js\b", r"\bnodejs\b"],
    "Django": [r"\bdjango\b"],
    "Flask": [r"\bflask\b"],
    "FastAPI": [r"\bfastapi\b"],
    "Docker": [r"\bdocker\b"],
    "Kubernetes": [r"\bkubernetes\b", r"\bk8s\b"],
    "AWS": [r"\baws\b", r"\bamazon web services\b"],
    "Azure": [r"\bazure\b"],
    "GCP": [r"\bgcp\b", r"\bgoogle cloud\b"],
    "Linux": [r"\blinux\b"],
    "REST": [r"\brest\b", r"\brestful\b"],
    "GraphQL": [r"\bgraphql\b"],
    "Pandas": [r"\bpandas\b"],
    "NumPy": [r"\bnumpy\b"],
    "Machine Learning": [r"\bmachine learning\b", r"\bml\b"],
    "CI/CD": [r"\bci/cd\b", r"\bcontinuous integration\b"],
}

PREFERRED_INDICATORS = (
    "preferred",
    "nice to have",
    "desirable",
    "bonus",
    "advantage",
)

RESPONSIBILITY_KEYWORDS = (
    "build",
    "develop",
    "maintain",
    "design",
    "implement",
    "test",
    "support",
    "collaborate",
    "create",
    "deploy",
    "manage",
    "improve",
)


def normalize_raw_job(
    raw_job: RawJobRecord,
    collected_at: datetime | None = None,
) -> NormalizedJob:
    """
    Convert one raw job record into the normalized Repo 2-compatible schema.
    """
    cleaned_description = clean_description(raw_job.description)
    combined_text = f"{raw_job.title}\n{cleaned_description}\n{raw_job.location}"

    required_skills, preferred_skills = extract_skills(combined_text)
    responsibilities = extract_responsibilities(cleaned_description)

    seniority = infer_seniority(raw_job.title)

    if seniority == "unknown":
        seniority = infer_seniority(cleaned_description)

    return NormalizedJob(
        job_id=build_job_id(raw_job),
        title=raw_job.title,
        company=raw_job.company,
        location=raw_job.location,
        work_type=infer_work_type(combined_text),
        seniority=seniority,
        description=cleaned_description,
        required_skills=required_skills,
        preferred_skills=preferred_skills,
        responsibilities=responsibilities,
        tags=infer_tags(combined_text, required_skills),
        source=raw_job.source,
        source_url=raw_job.source_url,
        collected_at=collected_at or datetime.now(timezone.utc),
        )


def normalize_raw_jobs(
    raw_jobs: list[RawJobRecord],
    collected_at: datetime | None = None,
) -> list[NormalizedJob]:
    """
    Convert multiple raw job records into normalized jobs.
    """
    return [
        normalize_raw_job(raw_job, collected_at=collected_at)
        for raw_job in raw_jobs
    ]


def build_job_id(raw_job: RawJobRecord) -> str:
    """
    Build a stable job ID from the source name and source-specific job ID.
    """
    source = sanitize_identifier(raw_job.source)
    source_job_id = sanitize_identifier(raw_job.source_job_id)

    return f"{source}_{source_job_id}"


def sanitize_identifier(value: str) -> str:
    """
    Convert an identifier into a lowercase underscore-separated string.
    """
    cleaned_value = value.strip().lower()
    cleaned_value = re.sub(r"[^a-z0-9]+", "_", cleaned_value)
    cleaned_value = cleaned_value.strip("_")

    return cleaned_value or "unknown"


def clean_description(description: str) -> str:
    """
    Remove simple HTML tags and normalize whitespace.
    """
    text = unescape(description)
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"\s+", " ", text)

    return text.strip()


def infer_work_type(text: str) -> str:
    """
    Infer work type from the job text.
    """
    normalized_text = text.lower()

    if "hybrid" in normalized_text:
        return "hybrid"

    if "remote" in normalized_text or "work from home" in normalized_text:
        return "remote"

    if (
        "on-site" in normalized_text
        or "onsite" in normalized_text
        or "office based" in normalized_text
        or "in office" in normalized_text
    ):
        return "onsite"

    return "unknown"


def infer_seniority(text: str) -> str:
    """
    Infer seniority from the job title and description.
    """
    normalized_text = text.lower()

    if re.search(r"\b(intern|internship)\b", normalized_text):
        return "intern"

    if re.search(r"\b(lead|principal|staff)\b", normalized_text):
        return "lead"

    if re.search(r"\b(senior|sr\.)\b", normalized_text):
        return "senior"

    if re.search(r"\b(mid|intermediate)\b", normalized_text):
        return "mid"

    if re.search(
        r"\b(junior|entry level|entry-level|graduate|trainee)\b",
        normalized_text,
    ):
        return "junior"

    return "unknown"


def extract_skills(text: str) -> tuple[list[str], list[str]]:
    """
    Extract required and preferred skills from job text.

    Skills found in sentences with preferred indicators are treated as
    preferred skills unless they also appear in required sentences.
    """
    required_skills: list[str] = []
    preferred_skills: list[str] = []

    for sentence in split_sentences(text):
        sentence_skills = find_skills_in_text(sentence)

        if not sentence_skills:
            continue

        if contains_preferred_indicator(sentence):
            add_unique_items(preferred_skills, sentence_skills)
        else:
            add_unique_items(required_skills, sentence_skills)

    preferred_skills = [
        skill for skill in preferred_skills if skill not in required_skills
    ]

    return required_skills, preferred_skills


def find_skills_in_text(text: str) -> list[str]:
    """
    Find known skills in a piece of text.
    """
    found_skills = []

    for skill, patterns in SKILL_PATTERNS.items():
        for pattern in patterns:
            if re.search(pattern, text, flags=re.IGNORECASE):
                found_skills.append(skill)
                break

    return found_skills


def contains_preferred_indicator(text: str) -> bool:
    """
    Return True if a sentence looks like it describes preferred skills.
    """
    normalized_text = text.lower()

    return any(indicator in normalized_text for indicator in PREFERRED_INDICATORS)


def extract_responsibilities(description: str) -> list[str]:
    """
    Extract simple responsibility sentences from the cleaned description.
    """
    responsibilities = []

    for sentence in split_sentences(description):
        normalized_sentence = sentence.lower()

        if any(keyword in normalized_sentence for keyword in RESPONSIBILITY_KEYWORDS):
            responsibilities.append(sentence)

    if not responsibilities and description:
        responsibilities.append(split_sentences(description)[0])

    return responsibilities[:5]


def infer_tags(text: str, skills: list[str]) -> list[str]:
    """
    Infer simple job tags from title, description, and extracted skills.
    """
    normalized_text = text.lower()
    tags = []

    if re.search(r"\b(backend|back-end|server-side|api|apis)\b", normalized_text):
        tags.append("backend development")

    if re.search(
        r"\b(frontend|front-end|react|user interface)\b",
        normalized_text,
    ):
        tags.append("frontend development")

    if re.search(
        r"\b(data|analytics|bi|business intelligence|pandas|sql)\b",
        normalized_text,
    ):
        tags.append("data")

    if re.search(
        r"\b(machine learning|ai|artificial intelligence)\b",
        normalized_text,
    ):
        tags.append("machine learning")

    if re.search(r"\b(cloud|aws|azure|gcp)\b", normalized_text):
        tags.append("cloud")

    if re.search(r"\b(docker|kubernetes|ci/cd|devops)\b", normalized_text):
        tags.append("devops")

    if skills or re.search(
        r"\b(software|developer|engineer|programmer|application developer)\b",
        normalized_text,
    ):
        tags.append("software engineering")

    return tags or ["general"]


def split_sentences(text: str) -> list[str]:
    """
    Split text into simple sentence-like chunks.
    """
    cleaned_text = clean_description(text)

    if not cleaned_text:
        return []

    sentences = re.split(r"(?<=[.!?])\s+|\n+", cleaned_text)

    return [sentence.strip(" -•") for sentence in sentences if sentence.strip(" -•")]


def add_unique_items(target: list[str], items: list[str]) -> None:
    """
    Append items to a list while preserving order and avoiding duplicates.
    """
    for item in items:
        if item not in target:
            target.append(item)