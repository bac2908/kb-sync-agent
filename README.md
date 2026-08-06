# Clinical RAG Quality Gate

A privacy-safe Product Engineering portfolio project for evaluating AI-generated
answers before they enter a clinical review workflow.

The project combines a production-style knowledge sync pipeline with a REST API
that checks RAG answers for source attribution, lexical grounding, and selected
high-risk certainty phrases. Every output still requires an explicit human review
decision: automated checks never establish clinical correctness.

> **Safety scope:** This is an educational prototype, not a medical device. It
> contains no patient data and must not be used for diagnosis or treatment.

## Why the public support corpus?

The repository originally synchronized public OptiSigns support articles from a
Zendesk REST API into Gemini File Search. That public corpus remains as a safe
surrogate for demonstrating ingestion, cleaning, chunking, delta detection, RAG,
and CI/CD without copying clinical data or protected health information (PHI).

The clinical quality-gate layer is domain-oriented, but its included examples are
synthetic workflow policies rather than medical claims.

## Product flow

```text
Public REST knowledge source
        |
        v
clean HTML -> Markdown -> SHA-256 delta -> Gemini File Search
                                                |
AI answer + retrieved evidence -----------------+
        |
        v
FastAPI quality gate -> automated checks -> PostgreSQL review queue
                                                |
                                                v
                                      clinician approve/reject
```

## Implemented capabilities

- Python knowledge ingestion from a paginated REST API with retry/backoff.
- RAG indexing with Gemini File Search and incremental upload checkpoints.
- Failure-safe manifests: a failed upload is retried on the next sync.
- FastAPI endpoints for evaluation, queue filtering, and clinical review.
- PostgreSQL in Docker Compose; SQLite is the zero-setup local fallback.
- Citation precision, evidence-overlap, and unsafe-certainty triage signals.
- A hard gate that prevents an automatically blocked output from being approved.
- Synthetic evaluation cases, 16 automated tests, Ruff, Docker, and GitHub CI.

See [JD alignment](docs/jd-alignment.md),
[architecture](docs/architecture.md), and
[clinical safety boundaries](docs/clinical-safety.md).

## Run locally

Requirements: Python 3.12.

```bash
python -m pip install -r requirements-dev.txt
python -m uvicorn src.api:app --reload
```

Open `http://127.0.0.1:8000/docs` for the interactive API documentation. Local
runs use `data/review_queue.db`, which is ignored by Git.

Run the synthetic oncology-workflow evaluation set:

```bash
python -m scripts.run_evaluation_cases
```

Run quality checks:

```bash
python -m ruff check .
python -m unittest discover -s tests -v
```

## Run with PostgreSQL

```bash
docker compose up --build
```

The API is available at `http://localhost:8000`; PostgreSQL remains inside the
Compose network.

## REST API

| Method | Endpoint | Purpose |
| --- | --- | --- |
| `GET` | `/health` | Verify API and database connectivity |
| `POST` | `/v1/evaluations` | Evaluate and enqueue an AI answer |
| `GET` | `/v1/evaluations?review_status=pending` | Read the human-review queue |
| `PATCH` | `/v1/evaluations/{id}/review` | Record clinician approval or rejection |

`case_id` accepts only a pseudonymous identifier such as `SYNTH-ONC-001`. The API
intentionally has no patient-name, email, phone, or free-form demographics field.

## Knowledge sync

Copy `.env.sample` to `.env`, configure Gemini, then run:

```bash
python main.py
```

The daily GitHub Actions workflow runs tests, fetches 30 public articles, uploads
only changed Markdown, and commits the new state after upload succeeds.

```env
ARTICLE_LIMIT=30
GEMINI_API_KEY=
GEMINI_FILE_SEARCH_STORE_NAME=
```

The sample assistant can be exercised with:

```bash
python src/test_gemini_assistant.py
```

## Known limitations

- Lexical overlap is an interpretable baseline, not a clinical-factuality metric.
- Authentication, RBAC, immutable audit logs, encryption policy, and migrations
  are required before any real clinical deployment.
- The current source adapter uses a non-clinical public corpus by design.
- Removed or updated remote Gemini documents still need stable document-ID
  lifecycle management; local removal is detected but not silently automated.
