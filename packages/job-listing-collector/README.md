# Job Listing Collector

Part of the **CareerVoice AI** portfolio project.

## Purpose

This repository collects job listing data from supported sources, normalizes the listings into a structured format, removes duplicates, and exports a `jobs.json` file compatible with the `preference-aware-job-recommender` repository.

```text
online job listing source
→ collect job information
→ clean / normalize it
→ deduplicate jobs
→ export structured jobs.json
```

## CareerVoice AI Context

The wider **CareerVoice AI** project is split into separate portfolio repositories:

```text
CareerVoice AI
├── voice-career-profile-extractor
├── preference-aware-job-recommender
└── job-listing-collector
```

Each repository has a focused responsibility:

```text
Repo 1: voice-career-profile-extractor
voice/text input → career_profile.json

Repo 3: job-listing-collector
job source → jobs.json

Repo 2: preference-aware-job-recommender
career_profile.json + jobs.json → ranked job recommendations
```

This repository is **Repo 3**. It only handles job listing collection and normalization.

## Scope

This repository focuses only on job listing collection and normalization.

It does not:

* extract career profiles from voice or text
* recommend jobs
* provide an API
* provide a web app
* connect all CareerVoice AI repositories into one system

## MVP Features

The current MVP supports:

* Adzuna source adapter
* environment-based API configuration
* raw job record model
* normalized job schema
* rule-based job normalization
* skill extraction
* work type inference
* seniority inference
* responsibility extraction
* tag inference
* job deduplication
* JSON export
* command-line interface
* example output file
* pytest test coverage
* ruff linting

## Source Policy

This project does not support arbitrary website scraping in the MVP.

Supported sources should be explicitly implemented as source adapters. The current MVP uses an Adzuna source adapter.

The project should not:

* bypass login pages
* bypass captchas
* bypass anti-bot systems
* collect from unsupported arbitrary websites
* hide or remove source attribution

Future source adapters should use clearly permitted APIs, feeds, or sources with explicit permission.

## Current Pipeline

The current pipeline is:

```text
Adzuna API
→ RawJobRecord
→ rule-based normalizer
→ NormalizedJob
→ deduplicator
→ jobs.json
```

The main command is:

```bash
uv run job-collect \
  --source adzuna \
  --query "software developer" \
  --query "backend developer" \
  --query "data analyst" \
  --location "Adelaide" \
  --max-results 5 \
  --output outputs/jobs.json
```
The `--query` option can be repeated to collect jobs for multiple search
queries in one run.

All collected jobs are combined, normalized, and deduplicated before one
`jobs.json` file is exported.

`--max-results` applies to each query. For example, three queries with
`--max-results 5` may collect up to 15 raw jobs before deduplication.

## Project Structure

```text
job-listing-collector/
├── .env.example
├── README.md
├── pyproject.toml
├── uv.lock
├── examples/
│   └── example_jobs.json
├── outputs/
│   └── jobs.json
├── src/
│   └── job_listing_collector/
│       ├── __init__.py
│       ├── cli.py
│       ├── config.py
│       ├── deduplicator.py
│       ├── exporter.py
│       ├── models.py
│       ├── normalizer.py
│       └── sources/
│           ├── __init__.py
│           ├── adzuna.py
│           └── base.py
└── tests/
```

Note: `outputs/jobs.json` is generated locally and is ignored by Git. The committed example output is stored in `examples/example_jobs.json`.

## Development

Install dependencies:

```bash
uv sync --dev
```

Run tests:

```bash
uv run pytest
```

Run linting:

```bash
uv run ruff check .
```

## Configuration

The Adzuna source adapter uses environment variables for API credentials.

Create a local `.env` file based on `.env.example`:

```bash
cp .env.example .env
```

Then fill in your own values:

```env
ADZUNA_APP_ID=your_adzuna_app_id
ADZUNA_APP_KEY=your_adzuna_app_key
ADZUNA_COUNTRY=au
```

Keep your `.env` file private and never share your real credentials.

## Usage

After configuring your local `.env` file, run:

```bash
uv run job-collect \
  --source adzuna \
  --query "software developer" \
  --location "Adelaide" \
  --max-results 5 \
  --output outputs/jobs.json
```

This command:

1. collects up to five raw jobs for each query from Adzuna
2. combines the results from all queries
3. converts them into normalized job records
4. removes duplicate jobs across all queries
5. exports one combined `outputs/jobs.json`

For a single-role search, provide `--query` only once.

You can also view CLI options with:

```bash
uv run job-collect --help
```

## Example Output

A committed example output file is available at:

```text
examples/example_jobs.json
```

This file shows the expected structure of the exported `jobs.json` file without requiring API credentials.

## Output Format

The exported `jobs.json` file contains a list of normalized job objects.

Example:

```json
{
  "job_id": "source_001",
  "title": "Junior Backend Developer",
  "company": "Example Tech",
  "location": "Adelaide",
  "work_type": "hybrid",
  "seniority": "junior",
  "description": "Build and maintain backend services.",
  "required_skills": ["Python", "SQL", "Git"],
  "preferred_skills": ["Docker", "AWS"],
  "responsibilities": ["Develop backend features"],
  "tags": ["backend development", "software engineering"],
  "source": "example_source",
  "source_url": "https://example.com/jobs/001",
  "collected_at": "2026-06-20T10:00:00Z"
}
```

## Normalized Job Fields

| Field              | Description                                                                     |
| ------------------ | ------------------------------------------------------------------------------- |
| `job_id`           | Stable ID generated from the source and source-specific job ID                  |
| `title`            | Job title                                                                       |
| `company`          | Company name                                                                    |
| `location`         | Job location                                                                    |
| `work_type`        | Normalized work type: `remote`, `hybrid`, `onsite`, or `unknown`                |
| `seniority`        | Normalized seniority: `intern`, `junior`, `mid`, `senior`, `lead`, or `unknown` |
| `description`      | Cleaned job description                                                         |
| `required_skills`  | Skills detected as required                                                     |
| `preferred_skills` | Skills detected as preferred or nice-to-have                                    |
| `responsibilities` | Extracted responsibility statements                                             |
| `tags`             | Simple tags inferred from title, description, and skills                        |
| `source`           | Source adapter name                                                             |
| `source_url`       | Original listing URL                                                            |
| `collected_at`     | Collection timestamp                                                            |

## Current Limitations

The MVP intentionally keeps the collection and normalization logic simple.

Current limitations:

* only the Adzuna source adapter is implemented
* only the first page of source results is collected
* rule-based skill extraction may miss skills hidden in long descriptions
* work type may remain `unknown` if the listing does not clearly mention remote, hybrid, or onsite
* seniority may remain `unknown` if the title and description do not contain clear seniority words
* no LLM-assisted normalization yet
* no scheduled collection yet
* no direct integration with Repo 2 yet

These limitations are planned future improvements rather than MVP blockers.

## Future Improvements

Possible future improvements include:

* more permitted source adapters
* pagination
* rate limiting
* source-specific parsers
* LLM-assisted normalization
* rule-based fallback when LLM normalization fails
* improved skill extraction
* better relevance filtering
* logging
* scheduled collection
* integration with Repo 2
