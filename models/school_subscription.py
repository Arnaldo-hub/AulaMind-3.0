"""
===========================================================
AulaMind Enterprise 3.0
models/school_subscription.py
-----------------------------------------------------------

Modelo SchoolSubscription

Suscripcion a nivel colegio/institucion.
Permite que un colegio pague una unica suscripcion
y todos sus docentes accedan a las funcionalidades
premium compartiendo un pool de generaciones.

Compatible con:
  SQLite
  PostgreSQL
  SQLAlchemy 2.x

Autor:
Biotecno Chile
===========================================================
"""

import uuid
from datetime import datetime

from sqlalchemy import String, ForeignKey, DateTime, Integer, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.base import Base


class SchoolSubscription(Base):

    __tablename__ = "school_subscriptions"

    # =====================================================
    # ID
    # =====================================================

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4())
    )

    # =====================================================
    # Relaciones
    # =====================================================

    school_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("schools.id"),
        nullable=False
    )

    plan_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("subscriptions.id"),
        nullable=False
    )

    # =====================================================
    # Estado
    # =====================================================

    status: Mapped[str] = mapped_column(
        String(20),
        default="trial",
        nullable=False
    )
    # trial | active | expired | cancelled

    starts_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True
    )

    ends_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True
    )

    # =====================================================
    # Limites
    # =====================================================

    max_teachers: Mapped[int] = mapped_column(
        Integer,
        default=10,
        nullable=False
    )

    price: Mapped[float] = mapped_column(
        Numeric(10, 2),
        default=49990.00,
        nullable=False
    )

    billing_cycle: Mapped[str] = mapped_column(
        String(20),
        default="monthly",
        nullable=False
    )
    # monthly | yearly

    generations_pool: Mapped[int] = mapped_column(
        Integer,
        default=100,
        nullable=False
    )

    generations_used: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False
    )

    # =====================================================
    # Auditoria
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
    # Relaciones ORM
    # =====================================================

    school = relationship(
        "School",
        back_populates="subscription"
    )

    plan = relationship(
        "Subscription",
        back_populates="school_subscriptions"
    )

    # =====================================================
    # Representacion
    # =====================================================

    def __repr__(self):
        return f"<SchoolSubscription({self.school_id} {self.status})>"

    # =====================================================
    # Serializacion
    # =====================================================

    def to_dict(self):
        return {
            "id": self.id,
            "school_id": self.school_id,
            "plan_id": self.plan_id,
            "status": self.status,
            "starts_at": self.starts_at.isoformat() if self.starts_at else None,
            "ends_at": self.ends_at.isoformat() if self.ends_at else None,
            "max_teachers": self.max_teachers,
            "price": float(self.price),
            "billing_cycle": self.billing_cycle,
            "generations_pool": self.generations_pool,
            "generations_used": self.generations_used,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
