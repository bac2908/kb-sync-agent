# Clinical safety boundaries

## Intended use

This prototype demonstrates how a Product Engineer can build a quality-control
workflow around an AI/RAG feature. It can prioritize outputs for review and retain
the evidence behind a decision.

It does not diagnose cancer, recommend therapy, calculate stage, interpret a
genomic variant, or validate clinical correctness.

## Human-in-the-loop contract

1. A caller submits a pseudonymous case ID, AI answer, and retrieved evidence.
2. Deterministic checks classify the answer as blocked or ready for review.
3. A qualified reviewer inspects the answer and its evidence.
4. The reviewer approves or rejects the record with an identity and notes.
5. Blocked records must be corrected and resubmitted; they cannot be approved.

The distinction between `ready_for_clinical_review` and `approved` is intentional.
Passing automated checks means only that the answer meets minimum product-quality
conditions.

## Data policy for this repository

- Do not submit names, phone numbers, emails, medical record numbers, dates of
  birth, addresses, or other patient identifiers.
- Use only synthetic identifiers such as `SYNTH-ONC-001`.
- Do not commit `.env`, local databases, exports, or raw external datasets.
- The checked-in examples contain no patient or clinical result data.

## Before real clinical use

- Threat model and complete security/privacy review.
- SSO, role-based access control, least privilege, and immutable audit trails.
- Encryption and key management for data in transit and at rest.
- Versioned clinical sources, provenance, retention, and deletion controls.
- Clinician-authored evaluation rubric and labeled validation dataset.
- Calibration by cancer type, language, and failure severity.
- Monitoring for drift, retrieval failures, latency, and reviewer disagreement.
- Regulatory and quality-management review appropriate to the intended use.
