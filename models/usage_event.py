import uuid
from datetime import datetime
from sqlalchemy import DateTime, ForeignKey, Integer, String, JSON
from sqlalchemy.orm import Mapped, mapped_column
from database.base import Base

class UsageEvent(Base):
    __tablename__ = "usage_events"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    school_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("schools.id"), nullable=True, index=True)
    event_type: Mapped[str] = mapped_column(String(60), nullable=False, index=True)
    feature: Mapped[str] = mapped_column(String(60), nullable=False, index=True)
    quantity: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    metadata_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False, index=True)
