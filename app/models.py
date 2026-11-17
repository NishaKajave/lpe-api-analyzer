from datetime import datetime, timezone
from sqlalchemy import String, Integer, Float, Text, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .database import Base

def utc_now() -> datetime:
    return datetime.now(timezone.utc)

class Analysis(Base):
    __tablename__ = "analyses"

    id: Mapped[int] = mapped_column(primary_key=True)
    test_name: Mapped[str] = mapped_column(String(200))
    endpoint: Mapped[str] = mapped_column(String(250))
    method: Mapped[str] = mapped_column(String(10), default="GET")
    expected_status: Mapped[int] = mapped_column(Integer, default=200)
    actual_status: Mapped[int] = mapped_column(Integer)
    error_message: Mapped[str] = mapped_column(Text)
    test_file: Mapped[str] = mapped_column(String(300), default="tests/api_test.py")

    status: Mapped[str] = mapped_column(String(40), default="PENDING")
    attempts_used: Mapped[int] = mapped_column(Integer, default=0)
    final_output: Mapped[str] = mapped_column(Text, nullable=True)

    validation_score: Mapped[int] = mapped_column(Integer, default=0)
    confidence_score: Mapped[int] = mapped_column(Integer, default=0)

    # Human review fields
    human_decision: Mapped[str] = mapped_column(String(30), nullable=True)
    comments: Mapped[str] = mapped_column(Text, nullable=True)
    reviewed_by: Mapped[str] = mapped_column(String(120), nullable=True)
    reviewed_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    rejection_reason: Mapped[str] = mapped_column(String(100), nullable=True)

    # Execution metadata & stop reason
    stop_reason: Mapped[str] = mapped_column(String(60), nullable=True)
    ai_engine: Mapped[str] = mapped_column(String(60), default="mock")
    model_name: Mapped[str] = mapped_column(String(120), default="Deterministic-Optimizer-Engine-v2")
    prompt_version: Mapped[str] = mapped_column(String(20), default="1.3")
    validator_version: Mapped[str] = mapped_column(String(20), default="1.2")
    processing_time: Mapped[float] = mapped_column(Float, default=0.0)
    masked_value_count: Mapped[int] = mapped_column(Integer, default=0)
    context_data: Mapped[str] = mapped_column(Text, nullable=True)

    # OpsZero & Live Data Integration Fields
    is_live: Mapped[bool] = mapped_column(default=False)
    live_url: Mapped[str] = mapped_column(String(500), nullable=True)
    latency_ms: Mapped[float] = mapped_column(Float, default=0.0)
    code_patch: Mapped[str] = mapped_column(Text, nullable=True)
    opszero_level: Mapped[str] = mapped_column(String(30), default="L2-Assisted")
    mttr_saved_minutes: Mapped[int] = mapped_column(Integer, default=35)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now)
    last_updated_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now, onupdate=utc_now)

    # Relationships
    attempts: Mapped[list["Attempt"]] = relationship("Attempt", back_populates="analysis", cascade="all, delete-orphan", order_by="Attempt.attempt_number")


class Attempt(Base):
    __tablename__ = "attempts"

    id: Mapped[int] = mapped_column(primary_key=True)
    analysis_id: Mapped[int] = mapped_column(ForeignKey("analyses.id", ondelete="CASCADE"))
    attempt_number: Mapped[int] = mapped_column(Integer)
    analyzer_output: Mapped[str] = mapped_column(Text)
    
    confidence_score: Mapped[int] = mapped_column(Integer, default=0)
    validation_score: Mapped[int] = mapped_column(Integer, default=0)

    # 5 Weighted category scores summing to 100
    required_fields_score: Mapped[int] = mapped_column(Integer, default=0)
    evidence_score: Mapped[int] = mapped_column(Integer, default=0)
    recommendation_score: Mapped[int] = mapped_column(Integer, default=0)
    safety_score: Mapped[int] = mapped_column(Integer, default=0)
    technical_score: Mapped[int] = mapped_column(Integer, default=0)

    validator_feedback: Mapped[str] = mapped_column(Text)
    attempt_status: Mapped[str] = mapped_column(String(40), default="RETRY_REQUIRED")

    started_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now)
    completed_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now)
    duration: Mapped[float] = mapped_column(Float, default=0.0)

    ai_engine: Mapped[str] = mapped_column(String(60), default="mock")
    model_name: Mapped[str] = mapped_column(String(120), default="Deterministic-Optimizer-Engine-v2")
    stop_reason: Mapped[str] = mapped_column(String(60), nullable=True)
    tokens_used: Mapped[int] = mapped_column(Integer, default=0)
    cost_estimate: Mapped[float] = mapped_column(Float, default=0.0)
    code_patch: Mapped[str] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now)

    analysis: Mapped["Analysis"] = relationship("Analysis", back_populates="attempts")


class Batch(Base):
    __tablename__ = "batches"

    id: Mapped[int] = mapped_column(primary_key=True)
    batch_id: Mapped[str] = mapped_column(String(80), unique=True, index=True)
    total_records: Mapped[int] = mapped_column(Integer, default=0)
    completed_records: Mapped[int] = mapped_column(Integer, default=0)
    passed_records: Mapped[int] = mapped_column(Integer, default=0)
    failed_records: Mapped[int] = mapped_column(Integer, default=0)
    status: Mapped[str] = mapped_column(String(30), default="STARTED")
    started_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now)
    completed_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    stopped_by: Mapped[str] = mapped_column(String(100), nullable=True)


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id: Mapped[int] = mapped_column(primary_key=True)
    analysis_id: Mapped[int] = mapped_column(Integer, nullable=True)
    batch_id: Mapped[str] = mapped_column(String(80), nullable=True)
    action: Mapped[str] = mapped_column(String(100))
    performed_by: Mapped[str] = mapped_column(String(100), default="System")
    details: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now)
