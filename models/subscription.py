"""
===========================================================
AulaMind Enterprise 3.0
models/subscription.py
-----------------------------------------------------------

Modelo Subscription

Compatible con:

✓ SQLite
✓ PostgreSQL
✓ SQLAlchemy 2.x

Autor:
Biotecno Chile
===========================================================
"""

import uuid
from datetime import datetime

from sqlalchemy import Boolean
from sqlalchemy import DateTime
from sqlalchemy import Integer
from sqlalchemy import Float
from sqlalchemy import String

from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship

from database.base import Base


class Subscription(Base):

    __tablename__ = "subscriptions"

    # =====================================================
    # ID
    # =====================================================

    id: Mapped[str] = mapped_column(

        String(36),

        primary_key=True,

        default=lambda: str(uuid.uuid4())

    )

    # =====================================================
    # Información del Plan
    # =====================================================

    name: Mapped[str] = mapped_column(

        String(100),

        nullable=False,

        unique=True

    )

    description: Mapped[str | None] = mapped_column(

        String(500),

        nullable=True

    )

    # =====================================================
    # Precios
    # =====================================================

    monthly_price: Mapped[float] = mapped_column(

        Float,

        default=0.0,

        nullable=False

    )

    yearly_price: Mapped[float] = mapped_column(

        Float,

        default=0.0,

        nullable=False

    )

    # =====================================================
    # Límites del Plan
    # =====================================================

    monthly_ai_requests: Mapped[int] = mapped_column(

        Integer,

        default=100,

        nullable=False

    )

    max_documents: Mapped[int] = mapped_column(

        Integer,

        default=100,

        nullable=False

    )

    max_storage_mb: Mapped[int] = mapped_column(

        Integer,

        default=500,

        nullable=False

    )

    max_exports_per_month: Mapped[int] = mapped_column(

        Integer,

        default=100,

        nullable=False

    )

    # =====================================================
    # Características
    # =====================================================

    allow_openai: Mapped[bool] = mapped_column(

        Boolean,

        default=True,

        nullable=False

    )

    allow_pdf_export: Mapped[bool] = mapped_column(

        Boolean,

        default=True,

        nullable=False

    )

    allow_word_export: Mapped[bool] = mapped_column(

        Boolean,

        default=True,

        nullable=False

    )

    allow_curriculum_engine: Mapped[bool] = mapped_column(

        Boolean,

        default=True,

        nullable=False

    )

    # =====================================================
    # Estado
    # =====================================================

    active: Mapped[bool] = mapped_column(

        Boolean,

        default=True,

        nullable=False

    )

    # =====================================================
    # Auditoría
    # =====================================================

    created_at: Mapped[datetime] = mapped_column(

        DateTime,

        default=datetime.utcnow,

        nullable=False

    )

    updated_at: Mapped[datetime] = mapped_column(

        DateTime,

        default=datetime.utcnow,

        onupdate=datetime.utcnow,

        nullable=False

    )

    # =====================================================
    # Relaciones
    # =====================================================

    users = relationship(

        "User",

        back_populates="subscription"

    )

    school_subscriptions = relationship(
        "SchoolSubscription",
        back_populates="plan"
    )

    # =====================================================
    # Representación
    # =====================================================

    def __repr__(self):

        return f"<Subscription({self.name})>"

    # =====================================================
    # Serialización
    # =====================================================

    def to_dict(self):

        return {

            "id": self.id,

            "name": self.name,

            "description": self.description,

            "monthly_price": self.monthly_price,

            "yearly_price": self.yearly_price,

            "monthly_ai_requests": self.monthly_ai_requests,

            "max_documents": self.max_documents,

            "max_storage_mb": self.max_storage_mb,

            "max_exports_per_month": self.max_exports_per_month,

            "allow_openai": self.allow_openai,

            "allow_pdf_export": self.allow_pdf_export,

            "allow_word_export": self.allow_word_export,

            "allow_curriculum_engine": self.allow_curriculum_engine,

            "active": self.active,

            "created_at": self.created_at.isoformat()

            if self.created_at else None

        }