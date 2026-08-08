# CareerVoice AI Web App

CareerVoice AI is a web application that turns a user's career information and preferences into structured, explainable job recommendations.

The application provides a browser-based interface over the existing CareerVoice AI pipeline. Users can write about their career, upload CVs and other career documents, speak through the browser microphone, review and correct the extracted information, search for current job listings, and receive ranked job recommendations with explanations.

## Current Status

CareerVoice AI currently supports an end-to-end multi-input workflow:

1. Provide career information
2. Generate a structured career profile
3. Review and edit the extracted profile
4. Configure job searches
5. Collect current job listings
6. Rank matching jobs
7. Review recommendation explanations
8. Download generated results

The web application currently supports:

- typed or pasted career information
- browser microphone recording
- speech transcription
- editable voice transcripts
- TXT document upload
- DOCX CV and document upload
- text-based PDF upload
- scanned or image-only PDF recognition
- optional additional career preferences alongside uploaded documents
- Standard career-profile extraction
- AI-assisted career-profile extraction
- editable profile review
- multiple target-role searches
- Adzuna job collection
- cross-query job deduplication
- Standard recommendation ranking
- AI-assisted recommendation ranking
- readable recommendation cards
- missing-skill and penalty explanations
- runtime capability preflight
- per-session workflow isolation
- responsive desktop, tablet, and mobile layouts
- mobile-friendly primary actions
- downloadable structured results

The current web MVP includes responsive desktop, tablet, and mobile layout refinement.

The next major milestone is deployment preparation.

---

## Features

### Career Information Input

Users can currently provide career information in three ways:

- **Write or paste** career information directly into the application
- **Upload a document** such as a CV or resume
- **Speak** using the browser microphone

All three input methods eventually converge into the same structured career-profile workflow.

```text
Write / paste ──────────────┐
                            │
Upload document ────────────┼─→ career text
                            │
Speak → transcription ──────┘
                                   ↓
                         profile extraction
                                   ↓
                         review and editing
```

---

## Write or Paste

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

---

## Browser Voice Input

Users can describe their career by speaking directly into the browser.

The current voice workflow is:

```text
browser microphone
→ WAV recording
→ voice validation
→ speech transcription
→ editable transcript
→ profile extraction
→ profile review
```

### Record Career Information

The browser provides a microphone control where users can record themselves describing:

- career background
- skills
- target roles
- preferred locations
- work preferences
- career goals
- constraints

The recording is captured as WAV audio.

Current voice recordings are limited to:

```text
10 MB
```

### Speech Transcription

Browser audio is passed through the existing CareerVoice AI transcription capability.

Repo 5 adapts browser audio into the interface already provided by the voice career-profile extractor.

Conceptually:

```text
browser WAV bytes
→ temporary WAV file
→ existing transcription service
→ cleaned transcript
```

The temporary audio file is removed automatically after the transcription operation.

### Editable Transcript

The application does not immediately convert a voice recording into a career profile.

Instead:

```text
voice
→ transcription
→ transcript review
→ user correction
→ profile extraction
```

Users can correct:

- names
- job titles
- skills
- technologies
- locations
- transcription mistakes
- misunderstood preferences

before continuing.

The edited transcript, rather than the original recording, is used for profile extraction.

This provides a human-review boundary between speech recognition and career interpretation.

### Voice Transcription vs Profile Extraction

Voice transcription and career-profile extraction are separate operations.

This allows:

```text
Voice
→ AI speech transcription
→ edited transcript
→ Standard profile extraction
```

as well as:

```text
Voice
→ AI speech transcription
→ edited transcript
→ AI-assisted profile extraction
```

Using voice therefore does not automatically require AI-assisted profile extraction.

The user still chooses how the reviewed transcript should be converted into a structured career profile.

---

## Upload a Career Document

Users can upload an existing CV, resume, or career document.

Supported document formats:

- `.txt`
- `.docx`
- text-based `.pdf`
- scanned or image-only `.pdf` through optional AI recognition

The application also provides an optional **Additional career preferences** field.

This is useful because a CV may explain:

```text
what the user has done
what skills the user has
what qualifications the user has
```

but may not explain:

```text
what role the user wants next
where the user wants to work
whether the user prefers hybrid or remote work
what the user wants to avoid
what requirements are non-negotiable
```

The document and additional preferences are therefore combined before career-profile extraction.

Example:

```text
Uploaded CV
+
"I want junior backend roles in Adelaide.
I prefer hybrid work and do not want senior positions."
        ↓
combined career information
        ↓
career-profile extraction
```

---

## Document Processing

Uploaded documents are converted into readable text before being passed through the existing career-profile extraction workflow.

Current support:

| Format | Support |
|---|---|
| TXT | Supported |
| DOCX | Supported |
| Text-based PDF | Supported |
| Scanned/image-only PDF | Supported with optional AI recognition |

### TXT

TXT files are decoded as UTF-8 text and normalized before profile extraction.

### DOCX

DOCX processing extracts:

- normal paragraphs
- table contents

Table support is useful because many CV templates store skills, education, employment dates, or other information inside Word tables.

### Text-Based PDF

For normal PDFs, CareerVoice AI first attempts local text extraction.

The PDF contents are converted into text without requiring AI document recognition.

Conceptually:

```text
Text-based PDF
→ local PDF text extraction
→ normalized text
→ career-profile extraction
```

### Scanned or Image-Only PDF

Some PDFs contain only page images and do not contain a selectable text layer.

CareerVoice AI detects this situation automatically.

When AI access is available, the user may explicitly enable:

```text
Allow AI recognition for scanned PDFs
```

The scanned-document flow is:

```text
Scanned PDF
     ↓
normal PDF text extraction attempted
     ↓
no readable text found
     ↓
render PDF pages as images
     ↓
AI document recognition
     ↓
recovered document text
     ↓
existing career-profile extraction
```

The current scanned-PDF recognition limit is:

```text
5 pages
```

This prevents unexpectedly large documents from creating excessive processing time or API usage.

### Explicit Permission for Scanned Documents

Normal text-based PDFs are read locally.

Scanned PDF pages are only sent to the configured AI service when:

1. the PDF has no readable text layer; and
2. the user enables **Allow AI recognition for scanned PDFs**.

Scanned-document recognition therefore does not happen silently.

### Document Recognition vs Profile Extraction

These are deliberately separate operations.

For example:

```text
Scanned PDF
→ AI document recognition
→ recovered text
→ Standard profile extraction
```

and:

```text
Scanned PDF
→ AI document recognition
→ recovered text
→ AI-assisted profile extraction
```

The document-recognition stage attempts to recover the original document text.

The profile-extraction stage is responsible for converting that text into structured career information.

This separation avoids mixing document transcription with career-profile interpretation.

---

## Career Profile Extraction

CareerVoice AI converts supplied career information into a structured career profile.

The profile can contain:

- target roles
- skills
- experience level
- preferred locations
- preferred work types
- liked areas
- disliked areas
- hard constraints
- career goals
- notes and uncertainties

Two profile-extraction approaches are currently supported.

### Standard Extraction

Standard extraction:

- is deterministic
- does not require an additional external AI request
- is useful for clearly structured information
- provides a fallback when AI-assisted extraction is unavailable

For voice input, transcription still requires the configured speech-to-text service, but the reviewed transcript can then be processed using Standard extraction.

### AI-Assisted Extraction

AI-assisted extraction uses an OpenAI model to interpret more flexible or complex career descriptions.

It is particularly useful for:

- natural-language career descriptions
- CV content
- voice transcripts
- mixed career history and preference information
- indirect or less structured input

AI-assisted functionality requires AI access configured by the application owner.

Normal end users do not enter the application owner's API key.

---

## Profile Review and Editing

Extracted information is not treated as automatically correct.

After profile creation, users can review and edit the structured profile before it affects job searching or recommendation ranking.

Editable fields currently include:

- target roles
- skills
- experience level
- preferred locations
- preferred work types
- areas the user likes
- areas the user wants to avoid
- non-negotiable requirements
- career goals
- notes and uncertainties

The workflow is:

```text
user input
→ extraction
→ structured profile
→ human review
→ confirmed profile
```

Human review is particularly important because:

- voice transcription may occasionally misunderstand speech;
- CVs may contain large amounts of historical information;
- current preferences may not be written in a CV;
- automated extraction may occasionally classify information imperfectly.

CareerVoice AI therefore keeps the user in control at two important stages.

For voice:

```text
Voice
→ review transcript
→ extract profile
→ review profile
```

For documents and typed input:

```text
Document / text
→ extract profile
→ review profile
```

---

## Job Search

After confirming the career profile, users can configure the job search.

The browser interface allows users to review or modify:

- roles to search for
- search location
- maximum listings per role
- job provider

Multiple target roles can be searched independently.

For example:

```text
junior software developer
backend developer
data analyst
```

become three separate job-search queries.

The maximum-results setting applies separately to each query.

Collected listings are then normalized and deduplicated before recommendation.

The current external job provider is:

```text
Adzuna
```

On wider screens, job-search settings can be displayed side by side:

```text
Search location | Maximum listings | Job provider
```

On narrower screens, these settings stack vertically.

---

## Job Recommendations

After collecting job listings, users can rank the jobs against their confirmed career profile.

The recommendation stage supports:

- Standard ranking
- AI-assisted ranking
- configurable maximum recommendation count
- optional hiding of jobs rejected by non-negotiable requirements

Recommendation results can include:

- rank
- job title
- company
- match score
- recommendation level
- matching skills
- reasons for the match
- missing skills
- penalties and concerns
- uncertainties
- non-negotiable requirement conflicts
- score details
- matching details

The goal is to provide explainable recommendations rather than simply returning unexplained ranking scores.

Recommendation summaries and recommendation-card headers use responsive layouts so information can wrap naturally on narrower screens.

---

## Downloadable Results

The application provides downloadable structured data at different stages of the workflow.

Current downloadable outputs include:

```text
career_profile.json
jobs.json
recommendations.json
```

This allows users to inspect or reuse the data generated by CareerVoice AI.

Download actions remain secondary to the main workflow actions and are sized according to their content.

---

## Runtime Capability Preflight

CareerVoice AI checks whether optional external capabilities are available before users attempt operations that require them.

Current capability checks include:

- OpenAI-backed functionality
- live job collection

### AI Unavailable

When OpenAI access is unavailable:

```text
Write / paste
→ available

TXT / DOCX / text-based PDF
→ available

Standard profile extraction
→ available

AI-assisted profile extraction
→ unavailable

Standard ranking
→ available

AI-assisted ranking
→ unavailable

Scanned PDF AI recognition
→ unavailable

Voice transcription
→ unavailable
```

Voice recording depends on speech transcription, so the voice workflow is disabled when the configured AI service is unavailable.

### Job Provider Unavailable

When the job provider is not configured:

```text
career information input
→ remains usable

career profile creation
→ remains usable

profile review
→ remains usable

live job search
→ disabled
```

This avoids making users wait for an external operation that is already known to be unavailable.

The normal user interface does not expose:

- API keys
- environment-variable names
- internal repository numbers
- command-line implementation details
- raw stack traces

---

## Architecture

CareerVoice AI Web App is the presentation layer of the wider CareerVoice AI system.

The existing projects remain responsible for their specialized capabilities.

### Career Profile Extraction

Responsible for:

```text
career text
→ structured career profile
```

Supports both Standard and AI-assisted extraction.

### Voice Transcription

The existing voice career-profile extractor provides the speech-transcription capability reused by the web application.

Repo 5 adapts browser-recorded WAV audio into that existing transcription interface.

```text
browser WAV
→ Repo 5 voice adapter
→ existing transcription component
→ transcript
```

### Job Listing Collection

Responsible for:

```text
job-search queries
→ external listings
→ normalization
→ deduplication
→ structured jobs
```

### Preference-Aware Recommendation

Responsible for:

```text
career profile
+
collected jobs
→ ranked and explainable recommendations
```

### Workflow Orchestration

Coordinates the existing profile extraction, job collection, and recommendation components.

### Web Application

Responsible for:

- browser forms
- browser microphone capture
- voice-input validation
- transcript review
- document upload
- document-to-text adaptation
- scanned-PDF recognition
- editable profile review
- responsive layout
- session state
- workflow progress
- safe error presentation
- job-search configuration
- recommendation configuration
- result presentation
- downloads

The web application does not rebuild the internal extraction, collection, recommendation, or transcription engines.

---

## Input Architecture

The current input architecture is:

```text
                         ┌─ Typed / pasted text
                         │
                         ├─ TXT
                         │
                         ├─ DOCX
User career information ┼─ Text-based PDF
                         │
                         ├─ Scanned PDF
                         │      ↓
                         │  AI document recognition
                         │
                         └─ Browser voice
                                ↓
                         speech transcription
                                ↓
                         transcript review
                                │
                                ▼
                       normalized career text
                                │
                                ▼
                    career-profile extraction
                                │
                                ▼
                       profile review/editing
                                │
                                ▼
                         job collection
                                │
                                ▼
                        recommendation
```

All supported input formats ultimately become career text before entering the existing profile-extraction pipeline.

---

## Separation of Responsibilities

Input processing is intentionally separated from career-profile interpretation.

### `document_input.py`

Responsible for deterministic document parsing:

```text
TXT
DOCX
text-based PDF
→ readable text
```

### `scanned_document.py`

Responsible for:

```text
scanned PDF
→ rendered page images
```

### `document_recognition.py`

Responsible for:

```text
page images
→ AI document recognition
→ recovered text
```

### `voice_input.py`

Responsible for:

```text
browser WAV
→ validation
→ VoiceRecording
```

Current validation includes:

- non-empty filename
- byte content
- non-empty recording
- WAV media type
- 10 MB maximum recording size

### `voice_transcription.py`

Responsible for adapting browser-recorded audio to the existing voice transcription component:

```text
VoiceRecording
→ temporary WAV
→ existing transcription API
→ cleaned VoiceTranscript
```

### Existing Career Profile Extraction

Responsible for:

```text
career text
→ structured career profile
```

This architecture keeps input-format handling independent from career interpretation.

---

## Responsive Interface

CareerVoice AI is designed to remain usable across desktop, tablet, and mobile browser widths.

Responsive behavior is implemented primarily with Streamlit's native layout components rather than custom viewport-specific JavaScript or fragile CSS overrides.

### Desktop

At wider browser sizes, the application can use multi-column layouts for related information.

Examples include:

```text
Target roles             Experience level
Skills                   Preferred locations
```

and:

```text
Search location | Maximum listings | Job provider
```

This makes better use of available desktop space.

### Tablet and Mobile

At narrower browser widths, form fields and layout elements are allowed to stack or wrap vertically.

The mobile workflow therefore becomes approximately:

```text
Career input
↓
Profile extraction
↓
Profile review
↓
Job-search configuration
↓
Job collection
↓
Recommendation configuration
↓
Recommendation cards
```

Primary workflow actions use the available width where appropriate.

Examples include:

```text
Transcribe recording
Generate career profile
Save and confirm profile
Search for jobs
Generate recommendations
```

This makes important workflow actions easier to interact with on narrow screens.

### Responsive Recommendation Cards

Recommendation summaries and card headers use layouts that can wrap when the available width becomes limited.

For example, a desktop card may appear approximately as:

```text
Junior Backend Developer                     82/100
Example Company
Recommendation level: Strong
```

while a narrow mobile layout can become:

```text
Junior Backend Developer
Example Company
Recommendation level: Strong

Match score
82/100
```

This avoids forcing job titles into excessively narrow columns.

### Profile Editing

Multi-value career-profile fields remain editable as text areas.

Fields containing more information can expand with their contents.

Fields such as:

```text
Target roles
Skills
Preferred locations
Preferred work types
Areas to avoid
```

remain multi-line controls because they may contain multiple values.

On narrow screens, profile-review columns stack vertically so users can edit the same profile without horizontal page scrolling.

### Primary Actions

Important actions are allowed to use the available width on narrow screens.

Examples include:

```text
Transcribe recording
Generate career profile
Save and confirm profile
Search for jobs
Generate recommendations
```

Secondary actions, such as downloading structured data, remain content-sized where appropriate.

### Native Browser Voice Control

Browser voice recording uses Streamlit's native audio-input control.

The application does not currently replace the microphone control with a custom mobile audio component.

This keeps the implementation maintainable and consistent with Streamlit's supported browser behavior.

A larger dedicated mobile recording control remains a possible future voice-interface improvement.

### Text Enlargement

CareerVoice AI relies on normal browser and operating-system text enlargement rather than providing a separate application-level font-size selector.

The interface is intended to remain usable when users enlarge browser content.

A dedicated in-app font-size preference is therefore not part of the current MVP.

### Responsive Testing

Responsive behavior is manually checked at representative widths such as:

```text
Desktop    approximately 1440 px
Tablet     approximately 768 px
Phone      approximately 393 px
```

Testing covers:

- input-method selection
- browser voice controls
- document upload
- profile review
- long profile values
- job-search settings
- primary actions
- download controls
- recommendation summaries
- recommendation cards
- text wrapping
- horizontal overflow

The current mobile layout has also been checked at an iPhone-sized viewport of approximately:

```text
393 × 852
```

Final responsive QA also includes checking enlarged browser content to ensure important controls remain visible and usable.

---

## Session Isolation

Every browser session receives a separate runtime workspace.

Conceptually:

```text
runtime/
└── sessions/
    └── <session-id>/
        ├── profile_input.txt
        ├── career_profile.json
        ├── jobs.json
        └── recommendations.json
```

The session identifier is validated before being used as a directory name.

Separate workspaces prevent users or browser sessions from accidentally overwriting each other's intermediate outputs.

Voice transcription uses a temporary audio file during the transcription operation, and that temporary file is removed automatically afterward.

---

## Stale Result Invalidation

Downstream results are invalidated when upstream information changes.

For example:

```text
new career profile
→ previous job search becomes stale
→ previous recommendations become stale
```

and:

```text
new job search
→ previous recommendations become stale
```

This prevents outdated results from being displayed as if they belong to the current workflow.

---

## Rerun Safety

Streamlit reruns application code when users interact with widgets.

CareerVoice AI avoids accidentally repeating expensive operations by:

- using forms
- requiring an explicit transcription action
- requiring explicit profile-generation submission
- storing results in Session State
- preserving the editable voice transcript in Session State
- using revision-based widget keys
- separating downloads from operation triggers
- invalidating downstream state when upstream data changes

Actions such as:

- reviewing a transcript
- editing profile fields
- opening an expander
- viewing profile data
- viewing score details
- downloading JSON results

should not automatically repeat transcription, extraction, job collection, or recommendation generation.

---

## Error Handling

Known workflow failures are converted into user-friendly browser messages.

Handled cases include:

- missing application runtime components
- empty career input
- empty voice recordings
- unsupported voice media types
- oversized voice recordings
- voice-transcription failures
- recordings with no recognized speech
- unsupported document formats
- oversized documents
- invalid TXT encoding
- invalid DOCX files
- invalid PDFs
- password-protected PDFs
- PDFs without readable text
- scanned-PDF recognition unavailable
- scanned PDFs exceeding the supported page limit
- AI document-recognition failures
- invalid career profiles
- missing target roles
- job-provider failures
- recommendation failures
- OpenAI service failures

Unexpected exceptions are logged for development while the browser receives a safe generic error message.

---

## AI Configuration

AI-backed features require an OpenAI API key.

For local development, create:

```text
.env
```

in the project root.

Example:

```env
OPENAI_API_KEY=your_api_key_here
```

The repository also provides:

```text
.env.example
```

which documents required configuration without containing real credentials.

Never commit the real `.env` file or API keys.

### AI-Backed Features

The configured OpenAI service may currently be used for:

- browser voice transcription
- AI-assisted career-profile extraction
- AI-assisted job recommendation
- scanned/image-only PDF recognition

These operations remain separate.

For example:

```text
Voice transcription
→ AI service

Reviewed transcript
→ Standard profile extraction
```

does not require a second AI profile-extraction request.

### Local Development

For local development:

```text
Repo 5 .env
→ application configuration
```

### Hosted Deployment

A hosted version should use:

```text
hosting platform secret storage
or
server-side environment configuration
```

API keys must remain server-side and must never be embedded in browser code.

Normal users should not be able to view the application owner's API keys.

---

## Job Provider Configuration

Job collection currently uses Adzuna.

Local configuration can include:

```env
ADZUNA_APP_ID=your_app_id
ADZUNA_APP_KEY=your_app_key
ADZUNA_COUNTRY=au
```

Real credentials must not be committed to Git.

---

## Requirements

- Python 3.11 or later
- `uv`
- local CareerVoice AI repositories required by the orchestration layer

Important Repo 5 dependencies include libraries for:

- Streamlit
- OpenAI access
- environment loading
- PDF text extraction
- PDF page rendering
- DOCX parsing

Development checks use:

- pytest
- Ruff

Black is not required.

---

## Installation

Clone the repository:

```bash
git clone <repository-url>
cd careervoice-ai-web-app
```

Install dependencies:

```bash
uv sync
```

---

## Local Repository Layout

During local development, the CareerVoice AI repositories are expected to exist as sibling projects.

Conceptually:

```text
CareerVoice-AI/
├── voice-career-profile-extractor/
├── preference-aware-job-recommender/
├── job-listing-collector/
├── careervoice-ai-orchestrator/
└── careervoice-ai-web-app/
```

The web application provides the browser experience while the orchestration layer and supporting repositories provide the existing domain functionality.

---

## Running the Application

Start Streamlit from the Repo 5 root:

```bash
uv run streamlit run app.py
```

The application is normally available locally at:

```text
http://localhost:8501
```

Stop the Streamlit server with:

```text
Control + C
```

---

## Example Workflows

### Typed Input

Choose:

```text
Write or paste
```

Enter:

```text
I am looking for junior software developer or backend developer roles
in Adelaide. I prefer hybrid work and have experience with Python,
SQL, Git, and REST APIs.
```

Then:

1. choose Standard or AI-assisted extraction;
2. generate the career profile;
3. review and edit the extracted information;
4. confirm the profile;
5. configure job-search roles;
6. select a location;
7. search for jobs;
8. select Standard or AI-assisted ranking;
9. generate recommendations;
10. inspect recommendation explanations.

### CV Upload

Choose:

```text
Upload a document
```

Upload:

```text
resume.docx
```

Optionally add:

```text
I want junior backend roles in Adelaide.
I prefer hybrid work and do not want senior positions.
```

Then generate and review the career profile.

### Scanned PDF

Choose:

```text
Upload a document
```

Upload an image-only PDF.

Enable:

```text
Allow AI recognition for scanned PDFs
```

The application performs:

```text
scanned PDF
→ page rendering
→ AI document recognition
→ recovered text
→ profile extraction
→ editable profile
```

### Browser Voice

Choose:

```text
Speak
```

Record something such as:

```text
I'm looking for a junior backend developer or software developer role
in Adelaide. I have experience with Python, SQL, and Git. I prefer
hybrid work and I don't want senior positions.
```

Then:

1. record the message in the browser;
2. click **Transcribe recording**;
3. review the generated transcript;
4. correct any transcription mistakes;
5. choose Standard or AI-assisted extraction;
6. generate the career profile;
7. review and edit the structured profile;
8. continue to job search.

For example:

```text
spoken:
"I want a role in Adelaide"

transcribed:
"I want a role in Adelaide"

user edits:
"I want a role in Melbourne"

profile extraction:
preferred_locations = Melbourne
```

This confirms that the reviewed transcript controls profile extraction.

---

## Testing

Run the complete automated test suite:

```bash
uv run pytest
```

The project includes tests covering:

- Streamlit application rendering
- browser voice input states
- voice-recording validation
- voice-transcription adaptation
- editable voice transcript workflow
- career-profile models
- document input
- TXT processing
- DOCX processing
- PDF text extraction
- scanned PDF page rendering
- AI document recognition
- scanned-document workflow fallback
- workflow services
- orchestration gateway behavior
- runtime configuration
- runtime dependency checks
- session workspace isolation
- UI state
- recommendation models
- recommendation UI
- project structure

Automated voice and document-recognition tests use fake or injected dependencies rather than making real external AI requests.

Real browser microphone behavior is verified separately through manual testing.

Manual browser testing also covers:

- desktop-width layout
- tablet-width layout
- phone-width layout
- long-text wrapping
- primary-button sizing
- download-button containment
- recommendation-card wrapping
- narrow-screen horizontal overflow
- enlarged browser content

---

## Development Checks

Before committing code, run:

```bash
uv run pytest
uv run ruff check .
git diff --check
```

All tests and checks should pass.

---

## Project Structure

A simplified current structure is:

```text
careervoice-ai-web-app/
├── app.py
├── README.md
├── pyproject.toml
├── uv.lock
├── .env.example
├── src/
│   └── careervoice_ai_web_app/
│       ├── __init__.py
│       ├── document_input.py
│       ├── document_recognition.py
│       ├── errors.py
│       ├── models.py
│       ├── orchestrator_gateway.py
│       ├── recommendation_models.py
│       ├── recommendation_ui.py
│       ├── runtime_check.py
│       ├── runtime_config.py
│       ├── scanned_document.py
│       ├── session_workspace.py
│       ├── ui_state.py
│       ├── voice_input.py
│       ├── voice_transcription.py
│       ├── web.py
│       └── workflow_service.py
└── tests/
    ├── test_app.py
    ├── test_document_input.py
    ├── test_document_recognition.py
    ├── test_models.py
    ├── test_orchestrator_gateway.py
    ├── test_project_setup.py
    ├── test_recommendation_models.py
    ├── test_recommendation_ui.py
    ├── test_runtime_check.py
    ├── test_runtime_config.py
    ├── test_scanned_document.py
    ├── test_session_workspace.py
    ├── test_ui_state.py
    ├── test_voice_input.py
    ├── test_voice_transcription.py
    └── test_workflow_service.py
```

---

## Design Principles

### User-Facing Language

The UI avoids exposing internal implementation terminology.

Instead of repository names and command-line concepts, users see language such as:

- Write or paste
- Upload a document
- Speak
- Transcribe recording
- Review your transcript
- Generate career profile
- Review and edit your career profile
- Search for jobs
- Generate recommendations
- Allow AI recognition for scanned PDFs

### Human Review Before Automation

Automatically generated information can be incomplete or inaccurate.

CareerVoice AI therefore introduces review stages where they are most useful.

For voice:

```text
speech
→ transcript
→ human review
→ profile
→ human review
```

For documents and typed input:

```text
career information
→ profile
→ human review
```

### Explainable Recommendations

CareerVoice AI aims to explain why a job was recommended instead of providing only a numerical score.

### Responsive by Default

The browser interface is designed so that the same workflow can be used from desktop, tablet, and mobile browsers.

Wide screens may use multi-column layouts, while narrower screens allow controls and information to stack or wrap.

Primary workflow actions expand where appropriate to provide larger interaction targets on narrow screens.

The implementation prefers native Streamlit layout behavior over device-specific JavaScript or fragile CSS overrides.

### Graceful Fallback

Where optional AI functionality is unavailable:

- typed career information remains available
- TXT, DOCX, and text-based PDFs remain usable
- Standard profile extraction remains available
- Standard recommendation ranking remains available
- scanned-PDF recognition clearly reports that AI access is required
- browser voice transcription clearly reports that AI access is required

### Privacy-Aware External AI Use

Text-based PDF parsing is performed locally.

Scanned PDFs are not sent for AI image recognition unless the user explicitly enables the scanned-PDF recognition option.

Browser voice recordings are sent to the configured speech-transcription service when the user explicitly requests transcription.

### Separation of Responsibilities

The web application handles user interaction and input adaptation.

The existing CareerVoice AI repositories continue to own:

- speech transcription
- career-profile extraction
- job collection
- recommendation
- orchestration

Repo 5 integrates these capabilities into one user-facing browser workflow.

---

## Planned Improvements

### Deployment Preparation

The next major milestone is preparing CareerVoice AI for hosted use.

Future deployment work will include:

- secure secret management
- API usage limits
- request throttling
- temporary-file cleanup
- production logging
- spending controls
- hosted configuration
- monitoring
- production error handling
- deployment documentation

### Additional Voice Improvements

Possible later voice improvements include:

- a larger dedicated mobile recording control
- clearer recording-duration guidance
- additional audio-upload formats
- transcription-language controls
- improved handling of long recordings
- more detailed transcription error feedback

### Additional Accessibility Improvements

Possible later accessibility improvements include:

- more extensive real-device accessibility testing
- keyboard-navigation review
- screen-reader review
- improved semantic descriptions where needed
- optional application-level display preferences if user testing shows a need

A dedicated font-size selector is not currently part of the MVP because normal browser and operating-system enlargement remain available.

### Additional Document Improvements

Possible later document enhancements include:

- improved handling of complex multi-column CV layouts
- expanded scanned-document page limits where appropriate
- additional document formats
- more structured extraction of education and certifications

### Additional Job Sources

The current web MVP uses Adzuna as the live job provider.

Future versions could add additional job sources behind the existing job-collection interface.

---

## CareerVoice AI

CareerVoice AI is designed around a simple idea:

> Users should be able to describe their career in the way that is most convenient for them, correct what the system understands, and receive job recommendations they can understand.

The current web application supports:

```text
Write
Upload
Speak
```

These input methods converge into the same structured and reviewable workflow:

```text
career information
→ normalized text
→ career profile
→ human review
→ live job search
→ explainable recommendations
```

The browser voice feature completes the original CareerVoice input concept, while responsive layout refinement allows the same workflow to remain usable across desktop, tablet, and mobile browser sizes.