# Architecture

## Product objective

Help a product or clinical team triage RAG answers consistently before a qualified
reviewer makes the final decision. The system separates deterministic engineering
checks from clinical judgment.

## Components

### Knowledge synchronization

`src/scraper.py` fetches a paginated public REST source, removes non-content HTML,
and writes normalized Markdown. SHA-256 hashes allow `src/delta.py` to classify
added, updated, removed, and unchanged records.

`src/gemini_uploader.py` uploads only changed files. It checkpoints every completed
upload. `main.py` commits the source manifest only after the upload phase succeeds,
so a transient provider failure does not make the next run skip missing content.

### Automated quality gate

`src/clinical_evaluation.py` receives the answer and the exact chunks retrieved by
the RAG system. It calculates:

- citation precision: whether cited URLs are present in retrieved evidence;
- lexical evidence overlap: an interpretable grounding baseline;
- safety flags: a deliberately small list of certainty/instruction phrases.

The output is either `blocked` or `ready_for_clinical_review`. There is no
automated `approved` state.

### Review API and persistence

`src/api.py` exposes the evaluation and human-review workflow. SQLAlchemy keeps
the application portable between a local SQLite file and PostgreSQL. Each record
stores the submitted evidence, computed metrics, automated decision, reviewer,
notes, and timestamps.

## Failure behavior

| Failure | Behavior |
| --- | --- |
| Zendesk returns 429/5xx | Retry with exponential backoff |
| Gemini upload fails | Source manifest remains old; next run retries the delta |
| Later file fails in a batch | Earlier successful files remain checkpointed |
| Citation is absent or unknown | Evaluation is blocked |
| Reviewer tries to approve blocked output | API returns HTTP 409 |
| Database is unavailable | Health/evaluation request fails instead of losing data |

## Data boundaries

The API accepts a pseudonymous `case_id`; the schema has no patient identity
fields. The example dataset contains synthetic workflow text only. For a real
deployment, upstream de-identification, authentication, authorization, encryption,
retention, audit, and regulatory review are mandatory.

## Scaling decisions

PostgreSQL is sufficient for the transactional review queue. MinIO would be a
reasonable boundary for larger immutable evidence artifacts, Airflow for multiple
dependent ingestion/evaluation jobs, and ClickHouse for high-volume longitudinal
quality analytics. They are intentionally not included until those scale and
operational requirements exist.
