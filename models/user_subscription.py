"""
===========================================================
AulaMind Enterprise 3.0
models/user_subscription.py
-----------------------------------------------------------

Modelo UserSubscription

Suscripción concreta de un usuario: qué plan tiene,
cuándo empieza, cuándo vence y cuánto ha usado.

Es el corazón del portero comercial (trial 3 días /
planes pagados). Ver services/entitlements.py.

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

from sqlalchemy import DateTime
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import String

from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship

from database.base import Base


class UserSubscription(Base):

    __tablename__ = "user_subscriptions"

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

    user_id: Mapped[str] = mapped_column(

        String(36),

        ForeignKey("users.id"),

        nullable=False,

        unique=True,  # v1: una suscripción vigente por usuario

        index=True

    )

    subscription_id: Mapped[str] = mapped_column(

        String(36),

        ForeignKey("subscriptions.id"),

        nullable=False

    )

    plan = relationship("Subscription")

    # =====================================================
    # Estado y período
    # status: trial | active | expired | cancelled
    # =====================================================

    status: Mapped[str] = mapped_column(

        String(20),

        nullable=False,

        default="trial",

        index=True

    )

    starts_at: Mapped[datetime] = mapped_column(

        DateTime,

        nullable=False,

        default=datetime.utcnow

    )

    ends_at: Mapped[datetime] = mapped_column(

        DateTime,

        nullable=False

    )

    # =====================================================
    # Uso (trial: tope de generaciones)
    # =====================================================

    generations_used: Mapped[int] = mapped_column(

        Integer,

        nullable=False,

        default=0

    )

    # =====================================================
    # Origen: auto_trial | manual | mercadopago
    # =====================================================

    source: Mapped[str] = mapped_column(

        String(30),

        nullable=False,

        default="auto_trial"

    )

    # =====================================================
    # Correos automáticos enviados (anti-duplicados)
    # =====================================================

    warning_sent_at: Mapped[datetime | None] = mapped_column(

        DateTime,

        nullable=True

    )

    expired_sent_at: Mapped[datetime | None] = mapped_column(

        DateTime,

        nullable=True

    )

    # =====================================================
    # Auditoría
    # =====================================================

    created_at: Mapped[datetime] = mapped_column(

        DateTime,

        nullable=False,

        default=datetime.utcnow

    )

    updated_at: Mapped[datetime] = mapped_column(

        DateTime,

        nullable=False,

        default=datetime.utcnow,

        onupdate=datetime.utcnow

    )
