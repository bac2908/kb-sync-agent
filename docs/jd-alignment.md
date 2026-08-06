# Product Engineer Intern JD alignment

This document maps implemented evidence to the Gene Solutions Product Engineer
Intern role without claiming that the prototype is ready for clinical use.

| JD area | Evidence in this repository |
| --- | --- |
| Develop AI-powered products | RAG knowledge sync plus an answer-quality API |
| Work with clinical workflows | Explicit clinician review queue and decision gate |
| Validate AI outputs | Citation, grounding, safety flags, synthetic eval cases |
| Test and investigate issues | Failure-path tests, health endpoint, retry/checkpoint logic |
| Propose product improvements | Safety boundaries, known limitations, scaling decisions |
| Document findings | Architecture, deployment, safety, and review notes |
| Python and REST APIs | Python 3.12, FastAPI, Zendesk REST adapter |
| PostgreSQL | SQLAlchemy model with PostgreSQL Docker Compose service |
| Docker and CI/CD | Dockerfile, Compose, PR CI, scheduled sync workflow |
| LLMs, RAG, prompt engineering | Gemini File Search, constrained system prompt, citations |
| Model evaluation | Reproducible case set and measurable automated signals |

## Behaviors demonstrated

- **Extreme Ownership:** failure behavior is explicit and tested; manifests cannot
  advance past a failed delivery.
- **Bias Toward Delivery:** the API runs locally with SQLite in one command and with
  PostgreSQL through Compose.
- **Learn Fast, Learn Always:** limitations distinguish a baseline lexical metric
  from real clinical validation and identify a concrete validation roadmap.
- **Clarity of Intent:** automated triage and clinician approval use different
  states and responsibilities.
- **Act Now, Not Later:** the original ingestion demo was extended into a working,
  tested review workflow rather than documented as a hypothetical design.

## Technologies intentionally not forced into the MVP

MongoDB, ClickHouse, Airflow, and MinIO are named in the JD but adding every tool
would increase operational surface without a current requirement. The architecture
documents where each becomes useful. This keeps the product small enough to test
and deliver while showing awareness of the broader stack.

## Suggested interview demo

1. Run `docker compose up --build` and open `/docs`.
2. Submit the grounded example and show `ready_for_clinical_review`.
3. Remove its citation and show the record is blocked.
4. Try to approve the blocked record and show HTTP 409.
5. Run the test suite and explain the failed-upload manifest test.
6. Discuss what must change before using any real oncology data.
