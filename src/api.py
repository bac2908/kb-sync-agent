import json
from contextlib import asynccontextmanager
from datetime import datetime
from typing import Annotated, Literal

from dotenv import load_dotenv
from fastapi import Depends, FastAPI, HTTPException, Query, Request, status
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import select, text
from sqlalchemy.orm import Session

from src.clinical_evaluation import EvidenceChunk, evaluate_answer
from src.database import Base, create_database_engine, create_session_factory
from src.models import EvaluationRecord, utc_now

SERVICE_NAME = "clinical-rag-quality-gate"


class EvidenceInput(BaseModel):
    text: str = Field(min_length=1, max_length=20_000)
    source_url: str = Field(pattern=r"^https?://", max_length=2_000)
    source_title: str = Field(default="", max_length=500)


class EvaluationCreate(BaseModel):
    case_id: str = Field(
        min_length=1,
        max_length=100,
        pattern=r"^[A-Za-z0-9._-]+$",
        description="Pseudonymous case identifier; never submit patient identifiers.",
    )
    question: str = Field(min_length=1, max_length=10_000)
    answer: str = Field(min_length=1, max_length=30_000)
    evidence: list[EvidenceInput] = Field(min_length=1, max_length=20)


class ClinicalReviewUpdate(BaseModel):
    decision: Literal["approved", "rejected"]
    reviewer: str = Field(min_length=1, max_length=100)
    notes: str = Field(default="", max_length=10_000)


class EvaluationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    case_id: str
    question: str
    answer: str
    evidence: list[EvidenceInput]
    metrics: dict[str, float]
    automated_status: str
    blocking_reasons: list[str]
    safety_flags: list[str]
    review_status: str
    reviewer: str | None
    review_notes: str | None
    created_at: datetime
    reviewed_at: datetime | None


def _record_response(record: EvaluationRecord) -> EvaluationResponse:
    return EvaluationResponse(
        id=record.id,
        case_id=record.case_id,
        question=record.question,
        answer=record.answer,
        evidence=json.loads(record.evidence_json),
        metrics=json.loads(record.metrics_json),
        automated_status=record.automated_status,
        blocking_reasons=json.loads(record.blocking_reasons_json),
        safety_flags=json.loads(record.safety_flags_json),
        review_status=record.review_status,
        reviewer=record.reviewer,
        review_notes=record.review_notes,
        created_at=record.created_at,
        reviewed_at=record.reviewed_at,
    )


def get_session(request: Request):
    session = request.app.state.session_factory()
    try:
        yield session
    finally:
        session.close()


DatabaseSession = Annotated[Session, Depends(get_session)]


def create_app(database_url: str | None = None) -> FastAPI:
    engine = create_database_engine(database_url)
    session_factory = create_session_factory(engine)

    @asynccontextmanager
    async def lifespan(application: FastAPI):
        Base.metadata.create_all(engine)
        yield
        engine.dispose()

    application = FastAPI(
        title="Clinical RAG Quality Gate",
        version="1.0.0",
        description=(
            "Privacy-safe portfolio API for automated RAG checks and mandatory "
            "clinical review. It is not a diagnostic or treatment system."
        ),
        lifespan=lifespan,
    )
    application.state.session_factory = session_factory

    @application.get("/health")
    def health(session: DatabaseSession) -> dict[str, str]:
        session.execute(text("SELECT 1"))
        return {"status": "ok", "service": SERVICE_NAME}

    @application.post(
        "/v1/evaluations",
        response_model=EvaluationResponse,
        status_code=status.HTTP_201_CREATED,
    )
    def create_evaluation(
        payload: EvaluationCreate,
        session: DatabaseSession,
    ) -> EvaluationResponse:
        evidence = [EvidenceChunk(**item.model_dump()) for item in payload.evidence]
        result = evaluate_answer(payload.answer, evidence)
        result_data = result.to_dict()

        record = EvaluationRecord(
            case_id=payload.case_id,
            question=payload.question,
            answer=payload.answer,
            evidence_json=json.dumps(
                [item.model_dump() for item in payload.evidence], ensure_ascii=False
            ),
            metrics_json=json.dumps(result_data["metrics"]),
            automated_status=result.automated_status,
            blocking_reasons_json=json.dumps(result.blocking_reasons),
            safety_flags_json=json.dumps(result.safety_flags, ensure_ascii=False),
        )
        session.add(record)
        session.commit()
        session.refresh(record)
        return _record_response(record)

    @application.get("/v1/evaluations", response_model=list[EvaluationResponse])
    def list_evaluations(
        session: DatabaseSession,
        review_status: Annotated[
            Literal["pending", "approved", "rejected"] | None, Query()
        ] = None,
        limit: Annotated[int, Query(ge=1, le=100)] = 50,
    ) -> list[EvaluationResponse]:
        statement = select(EvaluationRecord).order_by(
            EvaluationRecord.created_at.desc()
        )
        if review_status:
            statement = statement.where(EvaluationRecord.review_status == review_status)
        records = session.scalars(statement.limit(limit)).all()
        return [_record_response(record) for record in records]

    @application.patch(
        "/v1/evaluations/{evaluation_id}/review",
        response_model=EvaluationResponse,
    )
    def review_evaluation(
        evaluation_id: str,
        payload: ClinicalReviewUpdate,
        session: DatabaseSession,
    ) -> EvaluationResponse:
        record = session.get(EvaluationRecord, evaluation_id)
        if record is None:
            raise HTTPException(status_code=404, detail="Evaluation not found")

        if payload.decision == "approved" and record.automated_status == "blocked":
            raise HTTPException(
                status_code=409,
                detail=(
                    "Blocked output cannot be approved. Correct the answer or "
                    "evidence and submit a new evaluation."
                ),
            )

        record.review_status = payload.decision
        record.reviewer = payload.reviewer
        record.review_notes = payload.notes
        record.reviewed_at = utc_now()
        session.commit()
        session.refresh(record)
        return _record_response(record)

    return application


load_dotenv()
app = create_app()
