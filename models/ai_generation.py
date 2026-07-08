import uuid
from datetime import datetime
from sqlalchemy import DateTime, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column
from database.base import Base

class AIGeneration(Base):
    __tablename__ = "ai_generations"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    document_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("documents.id"), nullable=True, index=True)
    feature: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    provider: Mapped[str] = mapped_column(String(50), default="openai", nullable=False)
    model: Mapped[str | None] = mapped_column(String(100), nullable=True)
    success: Mapped[bool] = mapped_column(default=True, nullable=False)
    latency_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)
    input_tokens: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    output_tokens: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    estimated_cost_usd: Mapped[float] = mapped_column(Numeric(12, 6), default=0, nullable=False)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False, index=True)
