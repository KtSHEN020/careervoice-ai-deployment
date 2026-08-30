# CareerVoice AI Deployment Packages

This directory contains the package snapshots used by the CareerVoice AI deployment repository.

Each package originated as a separate CareerVoice AI development/portfolio repository. They are assembled here so the complete application can be installed, tested, and deployed from one repository.

## Packages

### `voice-career-profile-extractor`

Provides:

- text-based career input
- voice transcription integration
- Standard career-profile extraction
- AI-assisted career-profile extraction
- structured `career_profile.json` output
- English and Simplified Chinese AI output control

### `preference-aware-job-recommender`

Provides:

- Standard job scoring
- AI-assisted semantic scoring
- hard-constraint handling
- recommendation explanations
- missing skills, penalties, and uncertainties
- English and Simplified Chinese recommendation explanations

### `job-listing-collector`

Provides:

- Adzuna job collection
- normalization
- multi-query collection
- deduplication
- structured `jobs.json` output

### `careervoice-ai-orchestrator`

Coordinates:

```text
career information
  -> career profile
  -> job collection
  -> recommendations
```

It also passes user-selected output language settings to the profile extractor and recommender.

### `careervoice-ai-web-app`

Provides the user-facing Streamlit application, including:

- approved-user OTP login
- CareerVoice authorization
- bilingual UI
- quota display and enforcement
- text, document, and browser voice input
- profile review/editing
- job-search configuration
- recommendation display
- downloadable structured results

## Deployment-package policy

These directories are deployment snapshots, not independent virtual environments.

Do not copy the following into package directories:

- `.env`
- `.streamlit/secrets.toml`
- API keys or passwords
- `.git` histories
- `.venv`
- runtime user data
- generated outputs
- build artifacts
- caches

## Development checks

From the deployment repository root:

```bash
uv sync
uv run pytest -q
uv run ruff check .
git diff --check
```

Because the deployment repository installs local package snapshots into `.venv`, package changes may require a refresh such as:

```bash
uv sync --reinstall-package <package-name>
```

before running integration tests.