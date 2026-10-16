# CareerVoice AI Deployment

CareerVoice AI is a browser-based job recommendation application that turns a user's career information and preferences into a structured career profile, searches current job listings, and generates explainable recommendations.

This repository integrates the CareerVoice AI application and five Python components.
The active application uses a React/TypeScript/Vite frontend in `frontend/` and
a FastAPI backend in `backend/`. Python dependencies are managed with `uv`
using the integrated packages under `packages/`.

The original component repositories remain separate development and portfolio
projects. Imported package copies may have diverged through integrated development;
the current checked-out code governs this application's behavior. See
[historical import records](docs/upstream_versions.md). Cross-repository
synchronization is never automatic and requires explicit authorization.

## Implemented application

The React/FastAPI application supports:

- approved-user access with passwordless email OTP sign-in
- Supabase Auth and PostgreSQL-backed CareerVoice authorization
- persistent per-user daily AI usage accounting and quota display
- English and Simplified Chinese interfaces
- text input, browser voice input, and TXT/DOCX/PDF career documents
- supported scanned-PDF recognition with explicit AI-recognition opt-in
- Standard and AI-assisted career-profile extraction
- Adzuna job collection, multiple profile-derived queries, and deduplication
- Standard and AI-assisted recommendation ranking with explanations

Documents are limited to 5 MiB and voice recordings to 10 MiB; additional format
and scanned-PDF recognition restrictions apply. Voice transcription, scanned-PDF
recognition, and AI-assisted processing require configured external AI access.

Structured result downloads are implemented in the retained Streamlit interface
for profiles, jobs, and recommendations. The React interface displays results
but does not currently implement result downloads.

These are implemented capabilities, not a claim that a particular hosted release
or its external integrations have been verified. See [deployment](#deployment).

## Application workflow

```text
Sign in
  -> choose English or Simplified Chinese
  -> provide career information through Text, Voice, or Document input
  -> extract a career profile
  -> review, edit, and confirm the profile and target roles
  -> search current jobs
  -> generate recommendations
  -> review explanations
```

Job-search roles come from the confirmed profile; there is no default target role
when the profile has none. Recommendation handling includes missing skills,
penalties, uncertainty, and hard constraints. Missing listing information is
treated as unknown rather than invented. Adzuna listing URLs may lead to external
job sites; those destinations are not additional integrated collection APIs.

## Components

| Integrated Python component | Role |
| --- | --- |
| `voice-career-profile-extractor` | Text/voice processing and Standard or AI-assisted profile extraction |
| `preference-aware-job-recommender` | Standard or AI-assisted ranking, explanations, missing skills, penalties, uncertainty, and hard constraints |
| `job-listing-collector` | Adzuna collection, normalization, and cross-query deduplication |
| `careervoice-ai-orchestrator` | Coordinates profile extraction, job collection, and recommendation generation |
| `careervoice-ai-web-app` | Retained Streamlit UI plus shared authentication, database, usage, localization, document, voice, and workflow services used by FastAPI |

The React UI and FastAPI HTTP layer are separate from these packages. Existing
component CLI capabilities remain available; their package READMEs document
component-specific usage.

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

Each ordinary user has a persistent daily AI allowance shared across their
AI-assisted operations. The FastAPI default is
**40 AI units per day**, configurable through `CAREERVOICE_DAILY_AI_UNIT_LIMIT`.
Administrator accounts marked `ai_quota_exempt` are exempt from the ordinary
limit; their usage is still recorded. Actual deployed limits and account
exemptions require operator confirmation.

Accounting uses UTC calendar dates, so a new daily allowance begins at
**00:00 UTC**.

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
- job-search count

Usage is persisted in PostgreSQL, so refreshing the browser or starting a new
application session does not reset the daily allowance. This does not imply
that profile, job, or recommendation results persist across browser reloads.

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

- `.env` and local `.env.*` files, including `.env.backend.local` and `frontend/.env.local`
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

Browser-visible configuration must contain only public values, including the
Supabase publishable key. Never put database credentials, API secrets, or Supabase
service-role/admin keys in `VITE_*` variables or frontend code. Administrative
Supabase credentials used for tester provisioning must remain outside the public
application runtime.

## Runtime configuration

### Browser-visible frontend configuration

Vite reads these names through `frontend/src/config.ts`; see
[frontend/.env.example](frontend/.env.example) for public configuration names.

| Variable | Requirement |
| --- | --- |
| `VITE_SUPABASE_URL` | Required for frontend authentication |
| `VITE_SUPABASE_PUBLISHABLE_KEY` | Required for frontend authentication; publishable key only |
| `VITE_API_BASE_URL` | API base URL; defaults to `http://127.0.0.1:8000` for local development; set the intended backend URL for hosted builds |

These values are browser-visible and are included in the frontend build.
Local frontend settings can be placed in ignored `frontend/.env.local`.

### Backend configuration

The authenticated workflow requires both Supabase authentication configuration
and a configured PostgreSQL database with the application schema. Supply those
authentication and database settings to the backend process before startup.
External credentials are required for the capabilities indicated below;
optional settings have defaults.

| Variable | Requirement |
| --- | --- |
| `SUPABASE_URL` | Required for backend authentication |
| `SUPABASE_PUBLISHABLE_KEY` | Required for backend authentication |
| `DATABASE_HOST` | Required for the application database |
| `DATABASE_PORT` | Required; integer from 1 to 65535 |
| `DATABASE_NAME` | Required for the application database |
| `DATABASE_USER` | Required for the application database |
| `DATABASE_PASSWORD` | Required for the application database |
| `DATABASE_SSLMODE` | Optional; defaults to `require` |
| `OPENAI_API_KEY` | Required for AI-assisted extraction/ranking, voice transcription, and scanned-PDF recognition |
| `ADZUNA_APP_ID`, `ADZUNA_APP_KEY` | Required for Adzuna job collection |
| `ADZUNA_COUNTRY` | Optional collector setting; defaults to `au` |
| `CAREERVOICE_ENVIRONMENT` | Optional; `development` (default), `test`, or `production` |
| `CAREERVOICE_DAILY_AI_UNIT_LIMIT` | Optional; positive integer, default `40` |
| `CAREERVOICE_CORS_ORIGINS` | Optional comma-separated allowed origins; defaults to `http://localhost:5173` and `http://127.0.0.1:5173` |

Hosted frontend origins must be allowed by the backend's CORS configuration.
The source defaults do not establish the current production settings.

Backend settings and authentication/database readers use the process environment.
Do not assume `.env.backend.local` is automatically loaded. Make the required
settings available through your local environment setup before starting FastAPI;
the startup command below does not load that file.

Do not place real credentials in this repository. Hosted backend secrets belong
in the hosting platform's secret storage or equivalent server-side environment
configuration.

## Database

CareerVoice AI currently uses PostgreSQL tables for:

- approved/authorized application users
- persistent daily usage counters

The migrations in `supabase/migrations/` define the application tables, Row Level
Security, and an atomic quota-consumption function, including quota exemptions.
Whether those migrations and runtime permissions are applied to a hosted database
requires operator confirmation.

## Local development

Prerequisites: Python 3.11 or newer, `uv`, and Node.js/npm. The checked-in
GitHub Pages workflow uses Node.js 22. Configure the frontend and backend as
described in [runtime configuration](#runtime-configuration); authentication
also requires provisioned Supabase access and an authorized application user.

### FastAPI backend

From the repository root:

```bash
uv sync
uv run uvicorn backend.app.main:app --reload
```

By default, Uvicorn serves the backend at `http://127.0.0.1:8000`. The runtime entry
point is `backend/app/main.py`; it adapts the integrated services to HTTP.

### React frontend

In a separate terminal, from `frontend/`:

```bash
npm ci
npm run dev
```

Use the local address printed by Vite. The default backend CORS origins cover
port 5173; if the frontend uses a different origin, configure it explicitly.
See the [frontend README](frontend/README.md) for frontend tools and configuration.

### Testing, linting, and builds

From the repository root, run the Python suite (root, backend, and integrated
package tests) and Python lint checks:

```bash
uv run pytest -q
uv run ruff check .
```

From `frontend/`:

```bash
npm test
npm run build
npm run lint
```

These run Vitest, TypeScript/Vite compilation, and ESLint respectively.
For frontend dependency changes, also run `npm audit` and review lockfile changes.

From the repository root, check whitespace:

```bash
git diff --check
```

### Legacy Streamlit compatibility

The previous Streamlit interface is intentionally retained. After installing
Python dependencies and configuring its required services, start it from the
repository root:

```bash
uv run streamlit run app.py
```

This starts the legacy interface, not the React/FastAPI application. Streamlit
includes structured profile, job, and recommendation downloads. Earlier
documentation described Streamlit Community Cloud hosting; its current live
status is not established by repository files.

## Deployment

The checked-in [GitHub Pages workflow](.github/workflows/deploy-pages.yml):

- runs on pushes to `feat/frontend-backend-migration` or manual dispatch
- uses Node.js 22 and runs `npm ci` followed by `npm run build` in `frontend/`
- supplies `VITE_API_BASE_URL`, `VITE_SUPABASE_URL`, and
  `VITE_SUPABASE_PUBLISHABLE_KEY` from GitHub Actions variables
- uploads `frontend/dist` and deploys the static frontend to GitHub Pages
- contains no explicit Vitest, ESLint, Python-test, or security-audit step

The [Vite configuration](frontend/vite.config.ts) uses
`/careervoice-ai-deployment/` as the build base path. GitHub Pages hosts the
frontend; it does not run the FastAPI backend.

Backend hosting has previously been reported as Render. No Render infrastructure
definition is checked in. The actual service URL, build/start settings,
environment configuration, applied migrations, deployed release, and current
availability require operator confirmation. The local development command above
is not a verified production start command.

The workflow describes configured deployment behavior, not proof of a successful
or currently available hosted release.

## Repository structure

```text
careervoice-ai-deployment/
├── .github/workflows/deploy-pages.yml
├── app.py                         # Legacy Streamlit entry point
├── backend/
│   ├── app/                       # FastAPI routes, runtime, and service adapters
│   └── tests/
├── frontend/
│   ├── src/                       # React UI, auth, API client, and translations
│   ├── package.json
│   ├── package-lock.json
│   └── vite.config.ts
├── packages/
│   ├── voice-career-profile-extractor/
│   ├── preference-aware-job-recommender/
│   ├── job-listing-collector/
│   ├── careervoice-ai-orchestrator/
│   └── careervoice-ai-web-app/
├── docs/upstream_versions.md       # Historical imports
├── scripts/
├── supabase/migrations/
├── tests/
├── pyproject.toml
└── uv.lock
```

## Repository role and status

This repository is the integration and deployment codebase for the active
React/FastAPI migration and retained Streamlit compatibility. The integrated
Python packages are local dependencies defined in `pyproject.toml`, not
automatically synchronized mirrors of the original repositories.

Implemented capabilities are described above. Current hosting state, external
service configuration, and live end-to-end behavior need separate verification.
