from datetime import UTC, datetime
from uuid import uuid4

from sqlalchemy import DateTime, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from src.database import Base


def utc_now() -> datetime:
    return datetime.now(UTC)


class EvaluationRecord(Base):
    __tablename__ = "evaluation_records"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid4())
    )
    case_id: Mapped[str] = mapped_column(String(100), index=True)
    question: Mapped[str] = mapped_column(Text)
    answer: Mapped[str] = mapped_column(Text)
    evidence_json: Mapped[str] = mapped_column(Text)
    metrics_json: Mapped[str] = mapped_column(Text)
    automated_status: Mapped[str] = mapped_column(String(40), index=True)
    blocking_reasons_json: Mapped[str] = mapped_column(Text)
    safety_flags_json: Mapped[str] = mapped_column(Text)
    review_status: Mapped[str] = mapped_column(
        String(20), default="pending", index=True
    )
    reviewer: Mapped[str | None] = mapped_column(String(100), nullable=True)
    review_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now
    )
    reviewed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
