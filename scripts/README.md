# Deployment Scripts

This directory is reserved for trusted CareerVoice AI deployment and maintenance scripts.

Appropriate uses include:

- synchronizing approved package files from the original component repositories
- administrative tester provisioning
- deployment validation
- database maintenance that should not run inside the public Streamlit application
- release preparation and repository cleanup

## Security requirements

Deployment scripts must never copy or commit:

- `.env`
- `.streamlit/secrets.toml`
- API keys
- database passwords
- Supabase secret/admin keys
- `.git` histories
- virtual environments
- runtime user data
- generated outputs
- caches

Administrative scripts that require privileged credentials must read them from trusted local/server-side configuration and must not print those credentials to the terminal or logs.

## Package synchronization

If package synchronization is automated, use an explicit allowlist of source files rather than copying whole repositories blindly.

A synchronization process should exclude at least:

```text
.git/
.venv/
.env
.streamlit/secrets.toml
__pycache__/
.pytest_cache/
.ruff_cache/
build/
dist/
runtime/
outputs/
```

After synchronization, run the deployment repository checks from the repository root:

```bash
uv sync
uv run pytest -q
uv run ruff check .
git diff --check
```