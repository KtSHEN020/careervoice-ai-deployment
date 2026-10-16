---
name: targeted-validation
description: Select focused CareerVoice AI regression checks for backend, frontend, and shared-package changes, and identify required pre-commit validation.
---

# Targeted validation

Root `AGENTS.md` takes precedence. Ponytail efficiency instructions never waive
required verification. Activating this skill does not authorize execution:
in read-only tasks, inspect configuration and propose commands only. Execute
checks only within the user's authorized scope. Preserve AGENTS.md approval,
security, and Git-safety requirements; never stage, commit, or deploy implicitly.

## Select checks

- Inspect the current branch, status, changed files (including untracked files),
  affected callers, interfaces, and fixtures. Choose the smallest existing test
  files that cover the behavior and its consumers; do not assume a filename
  alone proves coverage. Identify gaps instead of claiming untested coverage.
- Recheck root/package `pyproject.toml`, `frontend/package.json`, and Vite/Vitest
  configuration when selecting commands. Use the integrated root environment.
  `uv run` may synchronize dependencies; do not install or repair dependencies
  without applicable authorization. Investigate stale package imports before
  considering reinstallation. Use mocks/fixtures rather than live services.

## Focused commands

Run Python commands from the repository root. Explicitly select its pytest
configuration to retain `--import-mode=importlib` despite nested package configs.
Select one relevant file, several files, or the affected suite; examples:

```bash
uv run pytest -c pyproject.toml -q backend/tests/test_job_search_api.py
uv run pytest -c pyproject.toml -q backend/tests
uv run pytest -c pyproject.toml -q packages/job-listing-collector/tests
uv run ruff check backend
uv run ruff check packages/job-listing-collector
```

For Ruff, narrow paths to changed Python files and relevant directories. Preserve
nested configuration discovery; do not force root settings over package rules.
Do not use formatting or autofix flags as validation.

Run frontend commands from `frontend/`; select the relevant existing Vitest file:

```bash
npm test -- src/api/client.test.ts
npm test -- src/auth/session-events.test.ts
```

These cover API authentication and session events, not component workflows.
There is no dedicated component/browser test setup in the audited configuration.
`npm run lint` already passes `.` to ESLint; appending a filename does not narrow
that script. Use the existing full lint/build commands when needed.

## Interface changes

Add affected producer/consumer package tests and relevant boundary tests:

- Profile extraction: `backend/tests/test_profile_integration.py`.
- Job search: `backend/tests/test_job_search_integration.py`.
- Recommendations: `backend/tests/test_recommendation_integration.py`.
- Shared workflow/orchestrator: web-app `test_workflow_service.py` and
  `test_orchestrator_gateway.py`, plus orchestrator `test_api.py`.

For example, from the repository root:

```bash
uv run pytest -c pyproject.toml -q backend/tests/test_profile_integration.py backend/tests/test_job_search_integration.py backend/tests/test_recommendation_integration.py
uv run pytest -c pyproject.toml -q packages/careervoice-ai-web-app/tests/test_workflow_service.py packages/careervoice-ai-web-app/tests/test_orchestrator_gateway.py packages/careervoice-ai-orchestrator/tests/test_api.py
```

These tests use fake external boundaries; job-search integration does not contact
Adzuna. Schema changes also need relevant `tests/test_database_schema.py`,
`tests/test_runtime_database_security.py`, and `tests/test_admin_quota_schema.py`;
these inspect SQL text, not a running database.

## Before proposing a commit

Focused checks supplement, not replace, AGENTS.md's applicable comprehensive
checks: Python `uv run pytest -q` and `uv run ruff check .` from root; frontend
`npm test`, `npm run build`, and `npm run lint` from `frontend/`. Run both sets
when both areas change, and include cross-package coverage for changed interfaces.
Frontend dependency changes also require `npm audit` and lockfile review within
authorized scope. The Pages workflow builds/deploys but supplies no test/lint gate.
Markdown-only changes need content/reference review and Git checks, not automatic
application test runs. Respect any task-specific execution restrictions.

Follow AGENTS.md's pre-commit Git checks: `git diff --check`, `git status --short`,
and `git diff --stat`; inspect working-tree and cached diffs plus untracked files.
Ordinary `git diff` omits new untracked files. Stop for guidance if checks fail;
do not commit with relevant failures or claim readiness while required checks
remain unexecuted. Avoid repeating successful checks unless subsequent changes
or unresolved concerns justify it.

## Report

Record exact commands and working directories, actual pass/fail/skip counts,
files changed, checks not run and why, coverage limitations, and remaining risks.
Distinguish planned commands from executed checks and focused passes from full
suite results. Do not reuse historical passing totals as current evidence.
