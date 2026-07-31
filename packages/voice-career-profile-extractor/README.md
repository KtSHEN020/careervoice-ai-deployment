# Voice Career Profile Extractor

Voice Career Profile Extractor is the first repository in the **CareerVoice AI** project suite.

The larger CareerVoice AI idea is a voice-based personalised job recommendation system. This repository focuses only on the first foundation layer:

```text
voice/text input → transcript handling → structured career profile JSON
```

This repository does **not** build the job recommendation system, API, or web application yet.

---

## Project Goal

The goal of this project is to extract a structured career profile from spoken or written career input.

The extracted profile includes more than skills. It can capture:

- target roles
- skills
- experience level
- preferred locations
- preferred work types
- liked areas
- disliked areas
- hard constraints
- career goals
- notes when information is missing or unclear

---

## Current MVP Features

- Load and clean transcript text from a `.txt` file
- Accept career preferences typed directly into the terminal
- Record career preferences from a microphone
- Transcribe recorded audio with the OpenAI Audio API
- Extract career profile information using either:
  - an offline rule-based extractor
  - an OpenAI-backed LLM extractor with structured output
- Store extracted information in a structured Python data model
- Export the profile as formatted JSON
- Run the project from the command line
- Test core functionality with `pytest`
- Check code quality with `ruff`
- Format Python code with `black`
- Manage dependencies with `uv`

---

## What This Project Does Not Include

This repository intentionally does not include:

- job recommendation logic
- job listing collection or scraping
- API service wrapper
- web application
- real-time streaming transcription
- browser-based voice recording
- advanced audio cleanup
- speaker diarization

Those features can be added in later repositories or future versions of the CareerVoice AI project suite.

---

## Example Input

File:

```text
examples/sample_input.txt
```

Example content:

```text
I am looking for a junior software developer role in Adelaide or remote.
I know Python, SQL, Git, basic React, and some machine learning.
I prefer backend or data-related roles.
I do not want sales roles, customer service roles, or senior roles.
My long-term goal is to move toward AI or software engineering.
```

---

## Example JSON Output

File:

```text
examples/sample_output.json
```

Example output:

```json
{
  "target_roles": [
    "junior software developer",
    "backend developer",
    "data analyst"
  ],
  "skills": [
    "Python",
    "SQL",
    "Git",
    "React",
    "machine learning"
  ],
  "experience_level": "junior",
  "preferred_locations": [
    "Adelaide",
    "remote"
  ],
  "preferred_work_types": [
    "remote"
  ],
  "liked_areas": [
    "backend development",
    "data-related roles",
    "AI tools",
    "software engineering"
  ],
  "disliked_areas": [
    "sales",
    "customer service",
    "senior roles"
  ],
  "hard_constraints": [
    "avoid sales roles",
    "avoid customer service roles",
    "avoid senior roles"
  ],
  "career_goals": [
    "move toward AI or software engineering"
  ],
  "notes": []
}
```

---

## Project Structure

```text
voice-career-profile-extractor/
├── examples/
│   ├── sample_input.txt
│   └── sample_output.json
├── src/
│   └── voice_career_profile_extractor/
│       ├── __init__.py
│       ├── audio_recorder.py
│       ├── audio_transcriber.py
│       ├── cli.py
│       ├── config.py
│       ├── exporters.py
│       ├── extractor.py
│       ├── llm_extractor.py
│       ├── models.py
│       └── transcript.py
├── tests/
│   ├── test_audio_recorder.py
│   ├── test_audio_transcriber.py
│   ├── test_cli.py
│   ├── test_config.py
│   ├── test_exporters.py
│   ├── test_extractor.py
│   ├── test_llm_extractor.py
│   ├── test_models.py
│   ├── test_project_setup.py
│   └── test_transcript.py
├── .env.example
├── .gitignore
├── pyproject.toml
├── uv.lock
└── README.md
```

---

## Installation

This project uses `uv` for dependency management.

Clone the repository:

```bash
git clone https://github.com/KtSHEN020/voice-career-profile-extractor.git
cd voice-career-profile-extractor
```

Install dependencies:

```bash
uv sync
```

### Configure OpenAI API access

Create a private local environment file from the provided template:

```bash
cp .env.example .env
```

Open `.env` and replace the placeholder with your own API key:

```text
OPENAI_API_KEY=your_api_key_here
```

The `.env` file is ignored by Git and must never be committed.

The OpenAI-backed LLM extractor and voice transcription modes may incur API usage charges.

---

## Usage

The CLI supports three input modes:

```text
file  = load an existing transcript text file
text  = type career preferences directly into the terminal
voice = record career preferences from the microphone
```

The CLI also supports two profile extractors:

```text
rules = offline rule-based profile extraction
llm   = OpenAI-backed profile extraction
```

The default profile extractor is `rules`.

### Load an existing transcript file

```bash
uv run career-profile-extract file examples/sample_input.txt
```

### Load a transcript file with LLM extraction

```bash
uv run career-profile-extract file examples/sample_input.txt --extractor llm
```

### Type career preferences directly into the terminal

```bash
uv run career-profile-extract text --extractor rules
```

### Type career preferences and save LLM-extracted JSON

```bash
uv run career-profile-extract text --extractor llm --output outputs/profile.json
```

### Record career preferences from the microphone

Install the optional microphone dependency:

```bash
uv sync --extra voice
```

Record speech, transcribe it, and use the rule-based profile extractor:

```bash
uv run --extra voice career-profile-extract voice --extractor rules
```

Record speech, transcribe it, use the LLM profile extractor, and save JSON:

```bash
uv run --extra voice career-profile-extract voice --extractor llm --output outputs/profile.json
```

The `voice` mode uses OpenAI audio transcription and therefore requires a configured `OPENAI_API_KEY`. It may incur API usage charges even when the rule-based profile extractor is selected.

The `llm` profile extractor also requires `OPENAI_API_KEY` and may incur an additional API usage charge.

---

## Python Usage

You can also use the package inside Python:

```python
from voice_career_profile_extractor import (
    extract_career_profile,
    load_transcript,
    profile_to_json,
)

text = load_transcript("examples/sample_input.txt")
profile = extract_career_profile(text)

print(profile_to_json(profile))
```

---

## Development

Run tests:

```bash
uv run pytest
```

Run code quality checks:

```bash
uv run ruff check .
```

Format code:

```bash
uv run black .
```

Recommended check before each commit:

```bash
uv run black .
uv run ruff check .
uv run pytest
```

---

## Current Extraction Approaches

The project supports two profile-extraction modes.

### Rule-based extractor

The offline rule-based extractor identifies configured keywords and preference phrases.

Example:

```bash
uv run career-profile-extract file examples/sample_input.txt --extractor rules
```

This mode is:

- offline
- deterministic
- explainable
- fast
- useful as a baseline and fallback

Its limitation is that it cannot reliably interpret every natural-language expression.

### LLM-backed extractor

The OpenAI-backed extractor sends transcript text to an LLM and requests a structured career profile.

Example:

```bash
uv run career-profile-extract text --extractor llm
```

This mode is more flexible when users express preferences in varied language. It is designed to extract only information supported by the user input and return the same stable JSON structure used by the rule-based extractor.

This mode requires a configured `OPENAI_API_KEY` and may incur API usage charges.

---

## Future Improvements

Possible future improvements include:

- real-time streaming transcription
- browser-based microphone input
- better handling of unclear or conflicting preferences
- confidence scores for extracted fields
- configurable speech-to-text models
- optional local transcription backend
- expanded rule dictionaries for offline extraction
- multilingual career-profile extraction
- optional Markdown summary output
- integration with a job recommendation engine
- API wrapper in a separate repository
- web interface in a separate repository

---

## CareerVoice AI Project Suite

This repository is planned as the first part of a larger project suite:

```text
Repository 1: voice-career-profile-extractor
Repository 2: preference-aware-job-recommender
Repository 3: job-listing-collector
Repository 4: careervoice-api
```

This repository only handles career profile extraction. Later repositories can reuse its JSON output as input for personalised job matching.