# CareerVoice AI Web App

CareerVoice AI is a browser-based application that turns a user's career information and preferences into structured, explainable job recommendations.

Users can write about their career, upload a CV or other career document, speak through the browser microphone, review and correct extracted information, search current job listings, and generate ranked recommendations with explanations.

The web application is integrated into the CareerVoice AI deployment repository and is designed for hosted use through Streamlit.

## Current status

The current MVP supports the complete end-to-end workflow:

1. Sign in with an approved email address
2. Choose English or Simplified Chinese
3. Provide career information
4. Generate a structured career profile
5. Review and edit the extracted profile
6. Confirm target roles and preferences
7. Configure job searches
8. Collect current job listings
9. Rank matching jobs
10. Review recommendation explanations
11. Download structured results

The current application includes:

- approved-user email OTP authentication
- sign-in and sign-out
- resend-code support with a cooldown
- persistent CareerVoice user authorization
- English and Simplified Chinese UI
- typed or pasted career information
- browser microphone recording
- speech transcription
- editable voice transcripts
- TXT document upload
- DOCX CV/document upload
- text-based PDF upload
- scanned/image-only PDF recognition
- optional additional preferences for uploaded documents
- Standard career-profile extraction
- AI-assisted career-profile extraction
- editable profile review
- multiple target-role searches
- Adzuna job collection
- cross-query deduplication
- Standard recommendation ranking
- AI-assisted recommendation ranking
- localized recommendation explanations
- persistent per-user AI usage quotas
- detailed per-feature AI usage counters
- runtime capability checks
- per-session workspace isolation
- downloadable JSON results
- responsive desktop, tablet, and mobile layout behavior

## User workflow

```text
Sign in
  -> choose language
  -> provide career information
  -> generate career profile
  -> review and edit
  -> confirm profile
  -> search for jobs
  -> generate recommendations
  -> review explanations
  -> download results
```

Career information can be provided through three input methods:

```text
Write or paste -----------+
                          |
Upload document ----------+--> career information
                          |        |
Speak -> transcription ---+        v
                             profile extraction
                                   |
                                   v
                             profile review
```

## Authentication and approved-user access

CareerVoice AI does not allow open self-registration.

Only approved users can access the application.

The sign-in flow is:

```text
approved email
  -> request login code
  -> receive OTP by email
  -> enter login code
  -> authenticate identity
  -> authorize CareerVoice user
  -> enter application
```

Authentication uses Supabase Auth with email OTP.

CareerVoice authorization is stored separately in PostgreSQL using a provider-independent application user ID. The application does not use the external authentication provider UUID as the CareerVoice primary user ID.

The login page supports:

- email-only sign-in
- no social-login requirement
- resend-code support
- resend cooldown
- using a different email before verification
- generic login responses that avoid revealing whether an email is approved

Signing out closes the authentication session and clears local user workflow state.

## Language support

The application supports:

- `ENG`
- `Simplified Chinese`

The selected language controls the user-facing interface, including:

- login and account controls
- career-information input
- profile review
- job-search configuration
- recommendation configuration
- recommendation cards
- quota information
- errors and status messages
- Standard recommendation explanations
- AI-generated human-readable explanations

The language selector changes presentation language without changing the machine-readable schema.

Structured JSON keys remain stable, for example:

```json
{
  "target_roles": [],
  "skills": [],
  "experience_level": null,
  "preferred_locations": [],
  "preferred_work_types": [],
  "liked_areas": [],
  "disliked_areas": [],
  "hard_constraints": [],
  "career_goals": [],
  "notes": []
}
```

This preserves compatibility across the CareerVoice AI packages.

For Australian job search, search-sensitive values such as role names, technology names, and locations remain canonical/search-friendly where appropriate even when the interface is in Simplified Chinese.

Changing the UI language does not silently regenerate previously created AI content. This avoids consuming additional AI allowance without explicit user action.

## Career information input

### Write or paste

Users can describe their career naturally, for example:

```text
I am looking for a junior software developer or backend developer role
in Adelaide. I prefer hybrid work. I have experience with Python, SQL,
Git, and REST APIs. I do not want senior positions.
```

Useful information can include:

- target roles
- technical skills
- work experience
- experience level
- preferred locations
- preferred work arrangements
- liked areas
- areas to avoid
- non-negotiable requirements
- career goals

Career text is length-limited before processing.

### Browser voice input

Users can speak directly through the browser microphone.

The current voice workflow is:

```text
browser microphone
  -> WAV recording
  -> recording validation
  -> speech transcription
  -> editable transcript
  -> profile extraction
  -> profile review
```

Voice transcription and career-profile extraction are separate operations.

This allows either:

```text
Voice
  -> AI transcription
  -> edited transcript
  -> Standard profile extraction
```

or:

```text
Voice
  -> AI transcription
  -> edited transcript
  -> AI-assisted profile extraction
```

Users can correct transcription mistakes before profile extraction begins.

### Upload a career document

Users can upload an existing CV, resume, or career document.

Supported document types include:

- TXT
- DOCX
- PDF

Text-based PDFs are parsed locally.

Scanned or image-only PDFs can optionally use AI-assisted document recognition. Scanned-document recognition is not triggered unless the user explicitly allows it.

Users can also provide additional career preferences alongside an uploaded document.

## Career-profile extraction

The application supports two profile-extraction modes.

### Standard extraction

Uses deterministic/rule-based extraction and does not require an AI model call.

### AI-assisted extraction

Uses the configured OpenAI service to interpret natural-language career information and produce the same structured career-profile schema.

The user reviews the generated profile before continuing.

Editable fields include:

- target roles
- skills
- experience level
- preferred locations
- preferred work types
- liked areas
- disliked areas
- hard constraints
- career goals
- notes

This human-review boundary prevents automatically generated information from being treated as final without user confirmation.

## Job search

After confirming the profile, users configure current job searches.

The current live job source is Adzuna.

The application supports:

- multiple target-role queries
- explicit location selection/input
- per-role result limits
- normalization
- cross-query deduplication

Search-sensitive profile values are kept suitable for current Australian job search where appropriate.

The public workflow currently limits:

- search roles per run
- job results per role
- total recommendations displayed

These safeguards prevent unexpectedly large downstream workloads.

## Recommendation generation

The application supports two ranking modes.

### Standard ranking

Uses deterministic scoring rules.

Standard ranking can explain factors such as:

- matched skills
- target-role alignment
- experience-level alignment
- location preference
- work-type preference
- liked areas
- career-goal support
- disliked-area penalties
- hard-constraint conflicts

These user-facing explanations are localized according to the selected application language.

### AI-assisted ranking

Uses the configured OpenAI service for semantic job-profile comparison.

AI-assisted ranking can provide:

- match reasons
- missing skills
- penalties
- uncertainties
- hard-constraint conflict evidence
- structured matched details

AI-generated explanations follow the selected output language while preserving machine-readable schema values and proper nouns where appropriate.

Hard-constraint rejection is validated defensively in application code rather than relying only on model-generated text.

## AI usage quota

AI-assisted operations share a persistent per-user daily allowance of:

```text
40 AI units per day
```

The allowance resets daily at:

```text
00:00 UTC
```

Current costs are:

| AI operation | Units |
| --- | ---: |
| AI-assisted career-profile extraction | 1 |
| Voice transcription | 1 |
| Scanned-document recognition | 1 |
| AI-assisted job ranking | 10 |

The interface displays:

- total units used
- total units remaining
- AI profile-extraction runs
- voice-transcription runs
- document-recognition runs
- AI-ranking runs

Usage is persisted per authorized CareerVoice user in PostgreSQL.

Refreshing the browser or starting a new Streamlit session therefore does not reset the daily quota.

Quota consumption is enforced atomically before an AI-assisted operation begins.

Standard non-AI features remain available when AI allowance is exhausted.

## Recommendation display

Recommendation cards can show:

- rank
- job title
- company
- match score
- recommendation level
- hard-constraint rejection status
- matched skills
- reasons
- missing skills
- penalties
- uncertainties
- optional score details
- optional match details

Users can download the recommendation document as JSON.

## Downloads

The application supports downloading structured outputs such as:

- career profile
- job recommendations

Downloaded JSON keeps stable schema keys regardless of UI language.

## Security and privacy

Never commit real credentials.

Secrets must remain server-side.

Examples of sensitive values include:

- OpenAI API keys
- Adzuna credentials
- database passwords
- Supabase secret/admin keys

The application owner's OpenAI key is never embedded in browser code.

Text-based PDF extraction is performed locally.

Scanned PDFs are only sent for AI recognition when the user explicitly enables that feature.

Browser voice recordings are sent to the configured transcription service only when the user requests transcription.

Temporary workflow files are isolated by application session and are not intended for Git tracking.

## Runtime configuration

The deployed application can require server-side values such as:

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

Do not place real values in source-controlled files.

The public runtime does not need an administrative Supabase secret key for normal user login.

Administrative tester provisioning should be performed through a trusted administrative workflow outside the public application.

## Database-backed user and usage model

CareerVoice AI stores application authorization separately from the external authentication provider.

The database includes application-level user records and persistent daily usage records.

The current design provides:

- provider-independent CareerVoice user IDs
- enabled/disabled user status
- mapping from authentication provider identity to CareerVoice user
- per-user daily AI usage
- per-feature usage counters
- atomic quota enforcement

## Requirements

- Python 3.11 or later
- `uv`
- Streamlit
- OpenAI SDK
- Supabase Python client
- PostgreSQL client support
- PDF text extraction/rendering support
- DOCX parsing support

Development checks use:

- pytest
- Ruff

Black is not required.

## Running from the deployment repository

From the `careervoice-ai-deployment` root:

```bash
uv sync
```

Because package snapshots are installed into the deployment virtual environment, changes to a package may require:

```bash
uv sync --reinstall-package careervoice-ai-web-app
```

or the corresponding changed package name.

Start the application:

```bash
uv run streamlit run app.py
```

The local Streamlit application is normally available at:

```text
http://localhost:8501
```

Stop the server with:

```text
Control + C
```

## Development checks

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

Do not commit while tests are failing.

## Hosted deployment

CareerVoice AI is designed to run as a dynamic Streamlit application.

GitHub stores the source repository, but GitHub Pages alone cannot run the Python/Streamlit backend.

The current hosted approach uses Streamlit Community Cloud, with secrets configured through hosted secret storage rather than committed files.

The hosted application relies on external services for enabled capabilities, including:

- Supabase Auth
- PostgreSQL
- email delivery for OTP
- OpenAI
- Adzuna

## Design principles

### User-facing language

The UI avoids exposing internal repository and command-line terminology.

Users see actions such as:

- Write or paste
- Upload a document
- Speak
- Transcribe recording
- Review your transcript
- Generate career profile
- Review and edit your career profile
- Search for jobs
- Generate recommendations

### Human review before automation

CareerVoice AI introduces review stages where automatically generated information could otherwise create downstream errors.

For voice:

```text
speech
  -> transcript
  -> human review
  -> profile
  -> human review
```

For documents and typed input:

```text
career information
  -> profile
  -> human review
```

### Explainable recommendations

The application explains why a job was recommended instead of presenting only a numerical score.

### Stable internal data

UI translations do not alter internal scorer identifiers or JSON schema keys.

For example, internal values remain:

```text
rules
llm
en
zh-CN
```

while the displayed labels are localized.

### Graceful fallback

When optional AI functionality is unavailable:

- typed career information remains available
- TXT, DOCX, and text-based PDFs remain usable
- Standard profile extraction remains available
- Standard recommendation ranking remains available
- AI-only features clearly report that AI access is required

### Responsive browser experience

The same workflow is intended for desktop, tablet, and mobile browsers using Streamlit's supported layout behavior.

## Deployment repository integration

Within `careervoice-ai-deployment`, the web package works together with:

```text
voice-career-profile-extractor
preference-aware-job-recommender
job-listing-collector
careervoice-ai-orchestrator
```

The web app owns user interaction and input adaptation. The supporting packages continue to own the underlying career-profile, job-collection, recommendation, and orchestration logic.

## Next improvements

The current MVP is deployable and usable by approved testers.

Further work can focus on:

- broader user testing
- accessibility review
- observability and production monitoring
- dedicated least-privilege production database credentials
- deployment/runbook documentation
- synchronization of finalized deployment fixes back to original component repositories
- additional job sources
- additional document formats
- improved long-recording handling
- further UI refinement based on tester feedback

## CareerVoice AI

CareerVoice AI demonstrates an end-to-end software-engineering workflow combining structured data processing, browser interaction, external APIs, AI-assisted features, security controls, persistence, testing, deployment, and user-facing explainability.