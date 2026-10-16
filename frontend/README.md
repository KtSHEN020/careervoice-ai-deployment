# CareerVoice AI Frontend

The React/TypeScript/Vite frontend provides email OTP sign-in, English and
Simplified Chinese interfaces, career-profile extraction and review, job search,
recommendations, and daily usage display. It calls the FastAPI backend for
application authorization and workflow processing.

See the root README for [shared architecture](../README.md#components),
[backend setup](../README.md#local-development), and
[security requirements](../README.md#security).

## Dependencies and tools

[package.json](package.json) defines the existing dependencies and scripts:

- React and React DOM for the UI
- `@supabase/supabase-js` for browser authentication and sessions
- TypeScript, Vite, and `@vitejs/plugin-react` for development and builds
- Vitest for tests
- ESLint with TypeScript, React Hooks, and React Refresh rules

The GitHub Pages workflow uses Node.js 22. Use the existing `package-lock.json`
with npm and the checked-in tool configuration.

## Public configuration and backend connection

Set local frontend settings in ignored `frontend/.env.local`. The public names
are listed in [.env.example](.env.example) and read by [src/config.ts](src/config.ts):

| Variable | Requirement |
| --- | --- |
| `VITE_SUPABASE_URL` | Required for frontend authentication |
| `VITE_SUPABASE_PUBLISHABLE_KEY` | Required for frontend authentication; publishable key only |
| `VITE_API_BASE_URL` | API base URL; defaults to `http://127.0.0.1:8000` locally; set the intended backend URL for hosted builds |

These values are browser-visible and included in the frontend build. Never use
private Supabase service-role/admin keys, database passwords, or external API
secrets here.

The FastAPI backend must be running and configured for Supabase authentication,
application-user authorization, and the services being used. Backend CORS must
allow the frontend origin; its local defaults cover port 5173. See the root
[runtime configuration](../README.md#runtime-configuration) for backend variables.

## Local development

From `frontend/`:

```bash
npm ci
npm run dev
```

Use the address printed by Vite. Start FastAPI in a separate terminal using the
[root instructions](../README.md#fastapi-backend).

## Tests, build, and lint

From `frontend/`:

```bash
npm test
npm run build
npm run lint
```

These run Vitest, TypeScript followed by Vite, and ESLint respectively.
The build output is `frontend/dist`. For frontend dependency changes, also run
`npm audit` and review lockfile changes.

## GitHub Pages deployment

The [deployment workflow](../.github/workflows/deploy-pages.yml) runs on pushes to
`feat/frontend-backend-migration` and manual dispatch. It uses Node.js 22, runs
`npm ci` and `npm run build`, and deploys `frontend/dist`. It supplies the three
`VITE_*` variables above from GitHub Actions variables; it does not
explicitly run tests, lint, or a security audit.

[vite.config.ts](vite.config.ts) sets the build base to
`/careervoice-ai-deployment/`. Pages serves the static frontend and requires a
separately hosted FastAPI backend. Current hosted URLs, variable settings, and
service availability require operator confirmation; the workflow alone does not
prove a successful live deployment.

## Interface compatibility

The React interface displays profiles, jobs, and recommendations but currently
has no result-download feature. Structured downloads remain available in the
[legacy Streamlit interface](../README.md#legacy-streamlit-compatibility).
