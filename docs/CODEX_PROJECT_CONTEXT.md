# CareerVoice AI — Codex Project Context

**Snapshot date:** 2026-10-16
**Basis:** `careervoice-ai-complete-review.zip`, archived committed tree plus two separately
included untracked Markdown files.
**Authority:** The current checked-out source, tests, migrations, and workflow configuration govern
implemented behavior. This file is a dated orientation aid, not an instruction to make changes.
`AGENTS.md` contains permanent agent rules.

## 1. Product goal and user flow

CareerVoice AI is a personal job-search and recommendation application with English and Simplified
Chinese UI. User workflow: approved email OTP sign-in → input career information (Text / Voice /
Document) → Standard or AI-assisted profile extraction → edit/confirm structured profile → Adzuna
job search using explicitly confirmed target roles → Standard or AI-assisted recommendations with
explanations.

User-facing UI should describe profile extraction, job search, and recommendations, rather than CLI
commands or numbered component repositories. Machine-readable API/schema keys remain stable
regardless of language.

## 2. Repository state and deployment

- GitHub repository: `KtSHEN020/careervoice-ai-deployment`.
- Development branch most recently verified by the user: `feat/frontend-backend-migration`.
- Latest user-verified commit: `7833eeb` — `fix: preserve workflow settings across navigation`.
- The user showed the local branch synchronized with `origin` and no tracked modifications as of
  October 16, 2026. The two instruction documents were **untracked**: `AGENTS.md` and
  `docs/CODEX_PROJECT_CONTEXT.md`.
- **The ZIP does not include `.git` metadata**: Codex must verify the branch, commit, and working
  tree *again in the user's local repository*. Do not claim those were proven by the archive.
- React frontend: GitHub Pages, `https://ktshen020.github.io/careervoice-ai-deployment/`.
- FastAPI backend: previously reported as hosted on Render,
  `https://careervoice-ai-api.onrender.com`. No Render infrastructure-as-code file was found in this
  snapshot; do not infer current Render settings from the ZIP.
- `.github/workflows/deploy-pages.yml` deploys the React frontend on pushes to the feature branch
  (or manual dispatch). It runs `npm ci` and `npm run build`, **but no Vitest, ESLint, Python tests,
  or security audit** in the workflow.
- The older Streamlit application is intentionally retained and is not the primary migration
  deployment. Do not remove without approval.
- Step 22B-1 hosted auth verification was explicitly confirmed. Step 22B-2 was committed/pushed but
  a separate hosted Step 22B-2D verification **was not explicitly confirmed** in the conversation;
  request/perform an authorized smoke test before claiming it passed.

## 3. Code organization and responsibilities

| Area | Primary source paths | Purpose |
| --- | --- | --- |
| React UI | `frontend/src/App.tsx`, `frontend/src/profile/`, `jobs/`, `recommendations/`, `layout/`, `usage/` | Profile → Jobs → Matches navigation and forms/results |
| Browser APIs | `frontend/src/api/` | Shared fetch client, typed request/response interfaces |
| Auth UI and token lifecycle | `frontend/src/auth/` | OTP, approved-user handoff, Supabase session refresh/sign-out events |
| Translations | `frontend/src/i18n.ts` | English and Simplified Chinese copy |
| Backend app | `backend/app/main.py`, `backend/app/api/v1/` | FastAPI factory, routes, health endpoint, dependency injection |
| Backend runtime/services | `backend/app/*_runtime.py`, `*_service.py`, `security.py` | Adapt shared workflows to authenticated HTTP requests |
| Shared Python | `packages/` | Five integrated career profile/job/recommendation/orchestration/web service packages |
| Supabase/PostgreSQL | `supabase/migrations/` | Application authorization and persistent usage/quotas |
| CI/deploy | `.github/workflows/deploy-pages.yml` | GitHub Pages frontend build and deployment |
| Legacy | `app.py`, `packages/careervoice-ai-web-app/app.py`, its `web.py` | Preserved Streamlit interface |

Five package directories: `voice-career-profile-extractor`, `job-listing-collector`,
`preference-aware-job-recommender`, `careervoice-ai-orchestrator`, `careervoice-ai-web-app`.

**Do not treat `careervoice-ai-web-app` as only legacy Streamlit:** FastAPI imports shared workflow,
database, usage, document, and voice modules from it. The original standalone repos are separate
portfolio projects. `docs/upstream_versions.md` records imported commits but its statement that
original repos *remain* sources of truth is outdated for integrated-package modifications; do not
automatically sync or overwrite copies.

## 4. Current functional baseline and constraints

- Auth: Supabase email OTP, app-level approved-user authorization; Supabase identity and CareerVoice
  app user UUID are distinct.
- `backend/app/config.py`: default ordinary daily limit **40 AI units**, configurable with
  `CAREERVOICE_DAILY_AI_UNIT_LIMIT`; database-based accounting and admin quota exemption are
  implemented.
- `packages/careervoice-ai-web-app/src/careervoice_ai_web_app/ai_usage.py`: AI profile extraction
  **1**, voice transcription **1**, document recognition **1**, AI ranking **10** units. Job search
  is recorded but not charged AI units. Inspect actual database charging behavior before changing
  semantics.
- Input: text; browser microphone transcription (voice upload limit 10 MiB); TXT, DOCX, PDF
  including supported scanned-PDF OCR (document upload limit 5 MiB). Further file
  validation/scanned-page restrictions apply.
- Job collection only uses the **Adzuna API**; returned URLs can lead to ViewJobs, the employer, or
  other destinations without any additional integrated API source.
- Roles come from the confirmed career profile; support multiple roles and deduplication. Do not
  introduce hard-coded default roles.
- Standard and AI-assisted ranking, uncertainty/explanations, hard-constraint rejection; maintain
  output language/schema contracts.
- `App.tsx` owns job and recommendation draft settings; navigating among steps retains them. Editing
  the profile or job search parameters invalidates dependent state; sign-out clears authenticated
  workflow. Browser reload is not yet a supported persisted-workflow feature.

## 5. Local development and verification

From the repository root:

```bash
uv sync
uv run pytest -q
uv run ruff check .
```

From `frontend/`:

```bash
npm ci  # on clean install only, when approved
npm test
npm run build
npm run lint
npm audit  # when needed, especially for dependency changes
```

Legacy Streamlit still has an entry point via `uv run streamlit run app.py`, but **this is not how
to run the current React/FastAPI UI**.

Local React: `cd frontend && npm run dev`. Local FastAPI: from repo root, after loading ignored
local config *without displaying secrets*, `uv run uvicorn backend.app.main:app --reload`. Local
frontend `VITE_API_BASE_URL` should point to `http://127.0.0.1:8000`. `frontend/.env.example`
documents public variable names (not secret values). Do not launch production integrations or
billable API operations in read-only tasks.

Historical user-reported baseline: **734 Python tests passed**, 5 SWIG/PyMuPDF-related dependency
warnings; **12 Vitest tests**, frontend build and ESLint passed; `npm audit` reported 0
vulnerabilities after remediation. These are historical reports, **not tests independently executed
during this ZIP audit**. Static inspection of this ZIP found **207 Python files**, all parsable with
Python's AST; this does not substitute for dependency-based tests.

Potential editable/install pitfall: when imported Python package files in `.venv/site-packages` lag
integrated source changes, inspect installation and, only if needed/approved, use `uv sync
--reinstall-package careervoice-ai-web-app`.

## 6. Confirmed source-code findings requiring later work

### Reliability — Step 22B-3 (after onboarding documentation)

- `frontend/src/api/client.ts`: authenticated requests now ask Supabase for the current token, but
  non-OK responses become generic `ApiError(status)` messages; network failures are not classified
  centrally. Existing frontend panels implement separate localized status-specific messages.
- `frontend/src/jobs/JobSearchPanel.tsx`: `handleSubmit()` invokes `onSearchInvalidated()`
  **before** validation and before the search finishes. `App.tsx` clears previously successful job
  results and dependent recommendation state. An unchanged-settings retry that fails can lose valid
  results.
- `frontend/src/recommendations/RecommendationPanel.tsx`: `handleSubmit()` invokes `onInvalidated()`
  at request start, clearing earlier recommendations before success. Differentiating unchanged retry
  versus edited settings is important: do not blindly preserve results for modified inputs.
- `backend/app/api/v1/jobs.py`: the route explicitly translates `ValueError` to 422 but not Adzuna
  `SourceError`. `packages/job-listing-collector/.../sources/adzuna.py` raises `SourceError` for
  HTTP errors, timeouts, or invalid upstream responses. Distinguish service failure mapping and safe
  message design from a demonstrated production outage.
- No automated React component-level tests for workflow navigation/failure recovery were found; only
  API client and session-event test files were present in the snapshot.

### Job data quality — planned Step 22C (separate)

- `packages/job-listing-collector/.../deduplicator.py`: URL-first key, title/company/location
  fallback only if URL absent; different destination URLs can allow near-duplicates. Two Funlab
  bartender records were *suspected* duplicates, not conclusively proven identical vacancies.
- `packages/job-listing-collector/.../normalizer.py`: `extract_responsibilities()` falls back to a
  description's first sentence if no duty keywords found; a Funlab marketing line was mistakenly
  shown as a responsibility.
- `packages/job-listing-collector/.../models.py`: `work_type` is remote/hybrid/onsite/unknown,
  **not** employment type (full-time/part-time/casual). Employment type is not separately structured
  in the current model.
- `packages/voice-career-profile-extractor/.../extractor.py`: the rule dictionaries emphasize
  software roles and do not recognize bartender and RSA. User tests confirmed this limitation;
  AI-assisted extraction handled the sample more effectively. Certification should eventually be
  distinct from skill.
- Adzuna returns a description field and a redirect URL; it does not automatically fetch the full
  employer advertisement. Missing duties, salary, schedule or qualifications must remain unknown
  unless supported by collected evidence.

## 7. Documentation and repository consistency — FIRST proposed Codex task

**This supersedes the former proposal to implement 22B-3 immediately.** First have Codex perform a
strictly **read-only, code-grounded documentation audit**, then, after separate approval, a narrowly
scoped documentation-only update. Only after that should Step 22B-3 code implementation begin.

Confirmed drift in the October 16 snapshot:

1. Root `README.md` calls Streamlit Community Cloud the *current deployment*, documents `uv run
   streamlit run app.py` as the primary startup, and omits the active React/FastAPI architecture and
   deployment path. Its description of synchronization with the original component repositories also
   conflicts with their later integrated development.
2. `frontend/README.md` is largely the Vite starter template, not project-specific instructions.
3. `docs/upstream_versions.md` records real historical import commit identifiers but concludes that
   the original component repositories remain authoritative; this needs a clarified *historical
   provenance vs current code ownership* statement. Preserve actual imported-commit data.
4. `packages/*/README.md` are largely standalone component documentation; many historical labels
   such as 'Repo 1/2/3/4' are appropriate for their independent project history. **Do not rewrite
   them wholesale** merely to make all READMEs identical. Identify material inaccuracies separately.
5. `README.md` lists result downloads as current, which is true of legacy Streamlit but **not
   confirmed in the React frontend**. Avoid marking planned export as implemented.
6. `.github/workflows/deploy-pages.yml` builds and deploys React on the migration branch but does
   not gate on tests/lint; documentation should state this accurately. Any CI improvement requires a
   separate approved change.
7. No Render infrastructure definition was found; external deployment secrets, domain settings,
   runtime start command, and current release status may need explicit user verification. Do not
   invent them.

Suggested documentation checkpoint (once approved): root `README.md`, `frontend/README.md`, and
`docs/upstream_versions.md` only. Scope may be narrowed after the audit. No code/dependency/config
edits mixed in.

## 8. Roadmap following documentation accuracy

- **22B-3:** API failures, actionable safe errors, recovery without misleading/stale results.
- **22C:** Job data quality: conservative deduplication, evidence-based responsibilities, employment
  type vs arrangement, possible structured provenance, test fixtures.
- **22D:** General-purpose profile extraction: occupation coverage, certifications/licences,
  experience and hard constraints.
- **22E:** Rate limits, upload limits, voice lifecycle, resilient external calls, security and quota
  semantics.
- **22F:** Job/match presentation, exports, accessibility, final UX.
- **22G:** Frontend regression coverage and CI quality gates.
- **22H:** Code cleanup, architecture/deployment documentation, release and Streamlit retirement decisions.

Do not begin roadmap items without a task-specific authorization.

## 9. Safe Codex collaboration

For the first task: read `AGENTS.md` and this context; verify actual project path, branch, latest
commit, Git status, and configurations. **Make zero edits**; do not run build/install/tests if they
might write files, and make no network or billable API calls. Cite code evidence for documentation
discrepancies, list unresolved operator questions, suggest smallest documentation update, then stop.
After approved edits, run scoped checks, inspect staged and unstaged diffs, and request separate
authorization before commits, pushes, deployment, or database actions.

**Maintenance:** Verify dated branch/build/live deployment claims at each milestone; update this
file after substantial changes and keep implementation facts grounded in current source.
