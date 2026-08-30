# CareerVoice AI Deployment

CareerVoice AI is a browser-based job recommendation application that turns a user's career information and preferences into a structured career profile, searches current job listings, and generates explainable recommendations.

This repository assembles the complete CareerVoice AI system into one deployable application. The original component repositories remain separate development and portfolio repositories; this deployment repository contains the tested package snapshots required to run the full application in one hosted environment.

## Current deployment

The application is deployed as a dynamic Streamlit web application.

Current deployment features include:

- Streamlit Community Cloud hosting
- approved-user access only
- passwordless email OTP sign-in
- Supabase Auth for authentication
- PostgreSQL-backed CareerVoice user authorization
- persistent per-user daily usage tracking
- AI usage quotas and counters
- English and Simplified Chinese interface support
- browser voice input
- TXT, DOCX, PDF, and scanned-PDF career-document support
- current job collection through Adzuna
- Standard and AI-assisted career-profile extraction
- Standard and AI-assisted recommendation ranking
- downloadable structured results

## Application workflow

The deployed application follows this user-facing workflow:

```text
Sign in
  -> choose ENG or Simplified Chinese
  -> provide career information
  -> generate career profile
  -> review and edit profile
  -> confirm target roles
  -> search current jobs
  -> generate recommendations
  -> review explanations
  -> download results
```

Career information can be provided by:

- writing or pasting text
- uploading a career document
- speaking through the browser microphone

## Components

The deployment repository contains snapshots of these CareerVoice AI components:

- `voice-career-profile-extractor`
  - text and voice input
  - Standard and AI-assisted career-profile extraction

- `preference-aware-job-recommender`
  - Standard and AI-assisted job ranking
  - recommendation explanations
  - missing-skill, penalty, uncertainty, and hard-constraint handling

- `job-listing-collector`
  - current job collection from Adzuna
  - normalization and cross-query deduplication

- `careervoice-ai-orchestrator`
  - coordinates profile extraction, job collection, and recommendation generation

- `careervoice-ai-web-app`
  - Streamlit user interface
  - authentication and authorization
  - quota display and usage enforcement
  - localization
  - document and voice input handling

## Authentication and access control

CareerVoice AI is not an open-registration application.

Access is limited to approved users.

The login flow is:

```text
approved email
  -> request login code
  -> email OTP
  -> verify Supabase identity
  -> verify CareerVoice app user
  -> enter application
```

The application supports:

- email-only OTP authentication
- no Google, Microsoft, or other social sign-in
- no public self-registration
- resend-code support with a cooldown
- sign-out that clears the local application session

Supabase Auth is used for authentication. CareerVoice maintains its own provider-independent application user ID in PostgreSQL rather than using the Supabase Auth UUID as the application's primary user identity.

## AI usage safeguards

AI-assisted operations share a persistent per-user daily allowance of:

```text
40 AI units per day
```

The allowance resets daily at:

```text
00:00 UTC
```

Current operation costs are:

| AI operation | Units |
| --- | ---: |
| AI-assisted career-profile extraction | 1 |
| Voice transcription | 1 |
| Scanned-document recognition | 1 |
| AI-assisted job ranking | 10 |

The application displays:

- total units used
- total units remaining
- AI profile-extraction count
- voice-transcription count
- document-recognition count
- AI-ranking count

Usage is persisted in PostgreSQL so refreshing the browser or starting a new Streamlit session does not reset the daily allowance.

Quota consumption is enforced atomically in the database before an AI-assisted operation begins.

## Language support

The interface supports:

- `ENG`
- `Simplified Chinese`

The selected language controls:

- login and account UI
- career-profile workflow UI
- job-search UI
- recommendation UI
- quota display
- Standard recommendation explanations
- AI-generated human-readable explanations

Machine-readable schema keys remain stable in English so the component packages remain compatible.

For Australian job search, search-sensitive values such as job roles, technologies, and locations remain canonical/search-friendly where appropriate even when the interface is in Simplified Chinese.

## Security

Never commit:

- `.env`
- `.streamlit/secrets.toml`
- API keys
- database passwords
- Supabase secret/admin keys
- virtual environments
- runtime user files
- generated outputs
- caches
- local IDE files

Hosted secrets must be configured through the hosting platform's secret storage or equivalent server-side environment configuration.

The public web runtime should use only the credentials it requires. Administrative Supabase credentials used for tester provisioning must remain outside the public application runtime.

## Runtime configuration

The hosted application requires server-side configuration for the capabilities that are enabled.

Typical settings include:

```text
OPENAI_API_KEY
ADZUNA_APP_ID
ADZUNA_APP_KEY
SUPABASE_URL
SUPABASE_PUBLISHABLE_KEY
DATABASE_HOST
DATABASE_PORT
DATABASE_NAME
DATABASE_USER
DATABASE_PASSWORD
DATABASE_SSLMODE
```

Do not place real values in this repository.

## Database

CareerVoice AI currently uses PostgreSQL tables for:

- approved/authorized application users
- persistent daily usage counters

The database also provides an atomic quota-consumption function used to enforce the daily AI allowance safely.

Row Level Security is enabled on the application tables.

## Local development

From the repository root:

```bash
uv sync
```

Start the application:

```bash
uv run streamlit run app.py
```

Run the full test suite:

```bash
uv run pytest -q
```

Run lint checks:

```bash
uv run ruff check .
```

Check whitespace errors:

```bash
git diff --check
```

## Repository structure

```text
careervoice-ai-deployment/
├── app.py
├── packages/
│   ├── voice-career-profile-extractor/
│   ├── preference-aware-job-recommender/
│   ├── job-listing-collector/
│   ├── careervoice-ai-orchestrator/
│   └── careervoice-ai-web-app/
├── scripts/
├── supabase/
├── tests/
├── pyproject.toml
└── uv.lock
```

## Repository role

This repository is the integration and hosting repository for CareerVoice AI.

Component development can continue in the original repositories, while approved versions are synchronized into this deployment repository for end-to-end testing and deployment.

Changes made directly in the deployment repository should be kept synchronized with the appropriate source repositories when they represent reusable component improvements.

## Current status

The deployed MVP now includes the complete end-to-end workflow, approved-user OTP authentication, persistent per-user usage accounting, AI cost safeguards, bilingual UI/output support, and cloud-ready configuration.

The next work should focus on user testing, deployment hardening, observability, and synchronization of finalized improvements back to the relevant component repositories.