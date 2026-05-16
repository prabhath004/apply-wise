# ApplyIntel

ApplyIntel is a local-first Chrome extension and FastAPI backend for job seekers. It captures a job posting, compares it with an uploaded resume, shows a fit score, summarizes public company context when available, and generates focused outreach text.

The project follows the PRD in `job_intelligence_extension_technical_prd.md`.

## What It Does

- Runs locally on your laptop.
- Uploads and parses PDF or TXT resumes.
- Captures LinkedIn job details with a defensive content script.
- Provides manual job input when page extraction is incomplete.
- Scores job fit with OpenAI using resume text, parsed job signals, seniority, responsibilities, education, domain, and risk factors.
- Generates outreach messages with OpenAI from the resume, job, fit analysis, company context, and selected contact.
- Stores resume, job, analysis, contacts, and outreach records in SQLite.
- Keeps the OpenAI API key in Chrome local storage by default.

## What It Does Not Do

- It does not auto-apply to jobs.
- It does not send emails or LinkedIn messages.
- It does not fabricate recruiter names, emails, sponsorship data, funding, or revenue.
- It does not scrape LinkedIn search pages or private data.
- It does not collect analytics.

## Privacy Model

All app data is local by default. The backend database lives at:

```txt
backend/data/applyintel.db
```

The extension stores settings in Chrome local storage. The preferred API key flow is BYOK: save the key in extension settings and send it to the local backend as `X-OpenAI-API-Key` for requests that need it. The backend settings route does not persist the API key unless explicitly requested by API payload.

## Backend Setup

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn main:app --reload --port 8000
```

Health check:

```bash
curl http://localhost:8000/health
```

## Extension Setup

```bash
cd extension
pnpm install
pnpm build
```

Then open Chrome:

1. Go to `chrome://extensions`.
2. Enable Developer mode.
3. Choose Load unpacked.
4. Select `extension/dist`.

For development, run:

```bash
cd extension
pnpm dev
```

## Basic Usage

1. Start the backend on `http://localhost:8000`.
2. Build and load the extension from `extension/dist`.
3. Open the extension settings and confirm the backend URL.
4. Add an OpenAI API key. Job analysis and outreach generation require it.
5. Upload a PDF or TXT resume from the sidebar.
6. Open a LinkedIn job page or paste job details manually.
7. Click Analyze Job.
8. Generate and copy outreach text after analysis.

## Tests

Backend:

```bash
cd backend
pytest
```

Extension:

```bash
cd extension
pnpm test
```

## Known Limitations

- Company intelligence is intentionally conservative and only summarizes from a directly available company URL.
- Contact discovery currently returns no contacts unless a future public-source provider is added.
- Resume parsing starts with local heuristics; OpenAI uses the extracted raw resume text during scoring and outreach.
- The extension targets Chrome and Chromium only.

## Contribution Guidelines

- Keep routes thin and put behavior in services.
- Use Pydantic schemas for API contracts.
- Keep TypeScript strict.
- Do not add fake data in execution paths.
- Do not log API keys or full resume text.
- Add tests for parsing, scoring, storage, and error handling changes.
