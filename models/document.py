import uuid
from datetime import datetime
from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, JSON
from sqlalchemy.orm import Mapped, mapped_column
from database.base import Base

class Document(Base):
    __tablename__ = "documents"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    school_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("schools.id"), nullable=True, index=True)
    document_type: Mapped[str] = mapped_column(String(40), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[str] = mapped_column(String(30), default="generated", nullable=False)
    course: Mapped[str | None] = mapped_column(String(120), nullable=True)
    subject: Mapped[str | None] = mapped_column(String(200), nullable=True)
    unit: Mapped[str | None] = mapped_column(String(255), nullable=True)
    topic: Mapped[str | None] = mapped_column(String(255), nullable=True)
    objectives_json: Mapped[dict | list | None] = mapped_column(JSON, nullable=True)
    input_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
