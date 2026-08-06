# Portfolio handoff checklist

## Repository quality

- [x] `.env` and local databases are ignored.
- [x] Runtime and development dependencies are pinned.
- [x] Ruff passes with the checked-in configuration.
- [x] Unit, API, and failure-path tests pass.
- [x] Synthetic evaluation cases pass reproducibly.
- [x] Pull requests and pushes run CI.

## Product demonstration

- [x] Knowledge is synchronized from a paginated REST API.
- [x] Changed content is uploaded through a RAG indexing provider.
- [x] Failed upload does not advance the source manifest.
- [x] AI answers are evaluated against the exact retrieved evidence.
- [x] Outputs missing citations or using unsafe certainty language are blocked.
- [x] A reviewer can approve or reject non-blocked outputs through REST APIs.
- [x] PostgreSQL deployment is defined with Docker Compose.

## Responsible healthcare framing

- [x] No patient data or real oncology result is checked in.
- [x] Synthetic case IDs are used throughout examples.
- [x] Automated checks are explicitly separated from clinical correctness.
- [x] Blocked outputs cannot be approved through the API.
- [x] Limitations and pre-production requirements are documented.

## Before sharing with an interviewer

1. Start Docker Desktop and run `docker compose up --build`.
2. Open `http://localhost:8000/docs` and rehearse the workflow in
   `docs/jd-alignment.md`.
3. Run `python -m ruff check .` and
   `python -m unittest discover -s tests -v`.
4. Confirm that no local `.env`, database, or credential is staged.
5. Replace screenshots only if they show the current API and contain no secrets.

The old OptiSigns screenshot and daily-run log remain as evidence of the original
public-corpus RAG pipeline. They are not clinical product evidence.
