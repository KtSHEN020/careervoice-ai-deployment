# Streamlit Configuration

This directory contains non-secret Streamlit configuration for the CareerVoice AI deployment.

## Secrets

Do not store real deployment secrets in this repository.

The file:

```text
.streamlit/secrets.toml
```

must not exist inside the repository and must never be committed.

For local development, secrets are stored outside the repository. For hosted deployment, secrets are configured through Streamlit Community Cloud or equivalent server-side secret storage.

Typical hosted runtime values include configuration for:

- OpenAI
- Adzuna
- Supabase public authentication
- PostgreSQL application access

Administrative Supabase secret keys used to provision approved testers must not be exposed to the public Streamlit runtime unless a trusted administrative operation explicitly requires them.

## Public configuration

Non-secret Streamlit settings may be stored in:

```text
.streamlit/config.toml
```

when required.

Any file added to this directory should be reviewed to confirm that it contains configuration only and no credentials, tokens, passwords, or private user information.