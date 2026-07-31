# Preference-Aware Job Recommender

A Python command-line tool that ranks structured job listings against a structured career profile using explainable preference-aware scoring.

This repository is the second component in the **CareerVoice AI** project suite.

CareerVoice AI is a voice-based personalised job recommendation system. The first repository, `voice-career-profile-extractor`, converts voice or text input into a structured career profile. This repository takes that profile and ranks structured job opportunities.

## Project Goal

The recommender takes:

```text
career_profile.json + jobs.json
```

and produces:

```text
ranked job recommendations with explainable scores
```

The recommender considers more than skill overlap. It can also evaluate target roles, experience level, preferred locations, work type preferences, liked areas, disliked areas, hard constraints, and career goals.

## Repository Scope

This repository focuses only on job recommendation logic.

It does **not** include:

* Voice transcription
* Career profile extraction
* Online job scraping
* Raw job-listing normalisation
* API backend
* Web frontend

The expected input job data should already be structured. In the larger CareerVoice AI system, online job collection and job-listing normalisation should be handled by a separate future repository.

## Scoring Modes

This project supports two scoring modes.

### LLM scoring

LLM scoring is the default mode.

```bash
uv run job-recommend
```

This is equivalent to:

```bash
uv run job-recommend --scorer llm
```

LLM scoring uses the OpenAI API to semantically compare the career profile with each structured job listing. It can better understand similar skills, related job titles, career-goal alignment, natural-language preferences, and nuanced hard constraints.

LLM mode requires a local `.env` file containing:

```text
OPENAI_API_KEY=your_api_key_here
```

### Rule-based scoring

Rule-based scoring is deterministic, offline, and does not require an API key.

```bash
uv run job-recommend --scorer rules
```

This mode uses transparent matching rules and is useful for testing, debugging, and comparing against the LLM scorer.

## MVP Features

* Load a structured career profile from JSON
* Load structured job data from JSON
* Support LLM-based semantic scoring
* Support rule-based deterministic scoring
* Rank jobs from strongest to weakest match
* Explain why each job was recommended
* Identify missing skills
* Apply penalties for disliked areas
* Detect hard-constraint conflicts
* Mark jobs rejected by constraints
* Optionally exclude rejected jobs
* Limit the number of returned recommendations
* Print readable results in the terminal
* Export structured recommendation results as JSON
* Show user-friendly CLI error messages
* Test rule-based and LLM-related logic with `pytest`

## Project Structure

```text
preference-aware-job-recommender/
├── examples/
│   ├── career_profile.json
│   └── jobs.json
├── src/
│   └── preference_aware_job_recommender/
│       ├── __init__.py
│       ├── cli.py
│       ├── config.py
│       ├── data_loader.py
│       ├── exporter.py
│       ├── llm_scorer.py
│       ├── models.py
│       ├── recommender.py
│       └── scoring.py
├── tests/
├── .env.example
├── .gitignore
├── README.md
├── pyproject.toml
└── uv.lock
```

## Requirements

* Python 3.11 or newer
* `uv`
* OpenAI API key for LLM mode

## Installation

Clone the repository:

```bash
git clone https://github.com/KtSHEN020/preference-aware-job-recommender.git
cd preference-aware-job-recommender
```

Install dependencies:

```bash
uv sync
```

## Environment Setup

Create a local `.env` file:

```bash
cp .env.example .env
```

Then edit `.env`:

```text
OPENAI_API_KEY=your_real_api_key_here
```

Do not commit `.env`.

Only `.env.example` should be committed.

## Quick Start

Run the default LLM scorer:

```bash
uv run job-recommend
```

Run the rule-based scorer without an API key:

```bash
uv run job-recommend --scorer rules
```

Show only the top three results:

```bash
uv run job-recommend --scorer rules --max-results 3
```

Hide jobs that conflict with hard constraints:

```bash
uv run job-recommend --scorer rules --exclude-rejected
```

Export results as JSON:

```bash
uv run job-recommend \
  --scorer rules \
  --max-results 3 \
  --exclude-rejected \
  --output outputs/recommendations.json
```

Use a specific LLM model:

```bash
uv run job-recommend \
  --scorer llm \
  --llm-model gpt-5.4-mini \
  --max-results 3
```

Use custom input files:

```bash
uv run job-recommend \
  --profile path/to/career_profile.json \
  --jobs path/to/jobs.json \
  --scorer rules
```

## Example Career Profile

The recommender accepts structured JSON output from the first CareerVoice AI repository:

```json
{
  "target_roles": [
    "junior software developer",
    "backend developer",
    "data analyst"
  ],
  "skills": [
    "Python",
    "SQL",
    "Git",
    "React",
    "machine learning"
  ],
  "experience_level": "junior",
  "preferred_locations": [
    "Adelaide",
    "remote"
  ],
  "preferred_work_types": [
    "remote"
  ],
  "liked_areas": [
    "backend development",
    "data-related roles",
    "AI tools",
    "software engineering"
  ],
  "disliked_areas": [
    "sales",
    "customer service",
    "senior roles"
  ],
  "hard_constraints": [
    "avoid sales roles",
    "avoid customer service roles",
    "avoid senior roles"
  ],
  "career_goals": [
    "move toward AI or software engineering"
  ],
  "notes": []
}
```

## Example Job Record

Repo 2 expects job data to already be structured:

```json
{
  "job_id": "job_001",
  "title": "Junior Backend Developer",
  "company": "Example Tech",
  "location": "Adelaide",
  "work_type": "remote",
  "seniority": "junior",
  "description": "Build and maintain backend services.",
  "required_skills": [
    "Python",
    "SQL",
    "Git"
  ],
  "preferred_skills": [
    "Docker",
    "AWS"
  ],
  "responsibilities": [
    "Develop backend features",
    "Work with relational databases",
    "Collaborate with the engineering team"
  ],
  "tags": [
    "backend development",
    "software engineering"
  ]
}
```

## Rule-Based Scoring Model

The rule-based scorer gives each job a positive score of up to 100 points:

| Factor                    | Maximum Points |
| ------------------------- | -------------: |
| Skill match               |             40 |
| Target role match         |             20 |
| Experience level match    |             10 |
| Preferred location match  |             10 |
| Preferred work type match |             10 |
| Liked area match          |              5 |
| Career goal match         |              5 |
| **Total**                 |        **100** |

Required skills receive a higher weight than preferred skills.

The rule-based scorer also applies penalties:

| Penalty                       | Points Deducted |
| ----------------------------- | --------------: |
| Each matched disliked area    |              15 |
| Each hard constraint conflict |              40 |

Disliked-area penalties are capped at 30 points. Hard-constraint penalties are capped at 80 points.

A job that conflicts with at least one hard constraint:

* Is marked as rejected by constraints
* Cannot receive a final match score above 25
* Can still appear in the output for explainability
* Can be hidden with `--exclude-rejected`

## LLM Scoring Model

The LLM scorer evaluates one structured job listing against one structured career profile.

It returns a structured evaluation containing:

* `job_id`
* `match_score`
* `role_alignment`
* `career_goal_alignment`
* `matched_skills`
* `missing_skills`
* `reasons`
* `penalties`
* `hard_constraint_conflicts`
* `uncertainties`

Python still enforces key output rules after the LLM response is parsed:

* The returned `job_id` must match the evaluated job
* Match scores must remain between 0 and 100
* Hard-constraint conflicts mark the job as rejected
* Rejected jobs cannot receive a final score above 25
* Recommendation levels are calculated consistently in Python

This keeps the LLM output useful while preserving predictable application behavior.

## Recommendation Levels

| Final Score | Recommendation Level |
| ----------- | -------------------- |
| 80–100      | `strong_match`       |
| 60–79       | `good_match`         |
| 40–59       | `partial_match`      |
| 0–39        | `poor_match`         |

## Example JSON Output

```json
{
  "recommendations": [
    {
      "job_id": "job_001",
      "title": "Junior Backend Developer",
      "company": "Example Tech",
      "match_score": 90,
      "recommendation_level": "strong_match",
      "reasons": [
        "Matches skills: Python, SQL, Git",
        "Matches target role: backend developer",
        "Matches experience level: junior"
      ],
      "missing_skills": [
        "Docker",
        "AWS"
      ],
      "penalties": [],
      "is_rejected_by_constraints": false,
      "scoring_method": "rules"
    }
  ],
  "total_jobs_scored": 7,
  "total_recommendations_returned": 7,
  "scoring_method": "rules"
}
```

## Error Handling

The CLI reports common input problems using readable error messages.

For example:

```bash
uv run job-recommend --profile missing.json --scorer rules
```

returns:

```text
Error: file not found: missing.json
```

If LLM mode is used without an API key:

```bash
uv run job-recommend --scorer llm
```

returns:

```text
Error: OPENAI_API_KEY is not set. Add it to a local .env file or export it in your terminal.
```

## Development

Run the test suite:

```bash
uv run pytest
```

Run Ruff:

```bash
uv run ruff check .
```

Check formatting:

```bash
uv run black --check .
```

Format the project when needed:

```bash
uv run black .
```

Run the rule-based workflow locally:

```bash
uv run job-recommend --scorer rules --max-results 3
```

Run the LLM workflow locally:

```bash
uv run job-recommend --scorer llm --max-results 1
```

## Current Status

The MVP recommender is complete and has been extended with optional rule-based and LLM-based scoring modes.

The current version uses structured sample job data. Online job collection and job-listing normalisation are intentionally left for a future repository.

## Future Improvements

* Configurable scoring weights
* More advanced rule-based text matching
* More sample profiles
* Expanded sample job datasets
* Markdown report export
* Batch LLM scoring
* Cost-aware LLM pre-filtering
* Online job collection in a separate repository
* API integration in a separate repository
* Web application integration in a separate repository
