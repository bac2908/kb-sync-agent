# Project review notes

## Evolution

The repository began as a compact knowledge-base synchronization take-home:

```text
Zendesk REST API -> clean Markdown -> Gemini File Search -> cited answer
```

It now uses that public, non-clinical corpus as a privacy-safe surrogate and adds
a Product Engineering workflow around AI output quality:

```text
answer + retrieved evidence -> automated quality gate -> clinician review queue
```

This evolution preserves working ingestion and deployment evidence while avoiding
the misleading claim that a portfolio project contains validated oncology data.

## Engineering decisions

- REST JSON is preferred over scraping rendered pages because it provides stable
  content metadata and pagination.
- HTML is cleaned and converted to Markdown before chunking and indexing.
- SHA-256 delta detection reduces unnecessary embedding work.
- The source manifest is committed only after upload succeeds.
- Upload state is checkpointed after each indexed file for safe batch recovery.
- FastAPI and PostgreSQL provide a small transactional review workflow.
- SQLite keeps the local setup fast; SQLAlchemy preserves the production boundary.
- Automated evaluation uses transparent baseline metrics and never emits a
  clinically approved state.

## Product decisions

- The API stores the evidence used for each answer so a reviewer can reproduce
  the context behind the automated result.
- Missing/unknown citations and selected unsafe-certainty phrases block delivery.
- Blocked answers must be corrected and resubmitted instead of manually overridden.
- The request schema intentionally omits patient identity and demographic fields.

## Current tradeoffs

- Lexical overlap is easy to explain and test but misses paraphrases and cannot
  measure medical correctness.
- Updated Gemini files are uploaded as new documents; stable remote document IDs
  are still required for clean replacement/deletion.
- The review record can be updated; a real system needs append-only audit events,
  authentication, and role-based authorization.
- Database schema creation is sufficient for a demo; production requires migrations.
- The public support source proves engineering behavior, not oncology knowledge.

## Next evidence to build

1. Clinician-authored rubric and a de-identified, governed evaluation dataset.
2. Retrieval metrics such as recall@k and answer metrics calibrated against reviewer
   labels.
3. Authentication, RBAC, immutable audit events, and provenance/version controls.
4. Provider document lifecycle management for update and deletion.
5. Observability for latency, errors, drift, and reviewer disagreement.
