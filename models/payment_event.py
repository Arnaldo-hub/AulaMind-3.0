"""
===========================================================
AulaMind Enterprise 3.0
models/payment_event.py
-----------------------------------------------------------

Modelo PaymentEvent (v3.2)

Registro de eventos de pago procesados desde el webhook
de Mercado Pago. Cumple dos funciones:

1. IDEMPOTENCIA: Mercado Pago puede reintentar o duplicar
   notificaciones. La llave única (provider + event_key)
   garantiza que cada cobro active/extienda el plan UNA
   sola vez.

2. AUDITORÍA: historial de qué evento llegó, para qué
   usuario y cuándo. Base del futuro panel comercial.

La tabla se crea sola al arrancar (create_all en boot).

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
from sqlalchemy import String

from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column

from database.base import Base


class PaymentEvent(Base):

    __tablename__ = "payment_events"

    # =====================================================
    # ID
    # =====================================================

    id: Mapped[str] = mapped_column(

        String(36),

        primary_key=True,

        default=lambda: str(uuid.uuid4())

    )

    # =====================================================
    # Qué evento fue
    # =====================================================

    # "mercadopago" (preparado para otros proveedores)
    provider: Mapped[str] = mapped_column(String(30))

    # Llave de idempotencia única, p.ej:
    #   "subscription_authorized_payment:1092837465"
    #   "subscription_preapproval:2c938084726fca"
    event_key: Mapped[str] = mapped_column(

        String(160),

        unique=True,

        index=True

    )

    # =====================================================
    # Para quién (puede quedar nulo si el evento llega sin
    # external_reference resoluble: se registra igual)
    # =====================================================

    user_id: Mapped[str] = mapped_column(

        String(36),

        index=True,

        nullable=True

    )

    # Acción resultante: "activated", "payment_failed",
    # "noted", "ignored", "duplicate"
    action: Mapped[str] = mapped_column(String(30))

    # Resumen legible (nunca datos de tarjeta)
    detail: Mapped[str] = mapped_column(

        String(500),

        default=""

    )

    created_at: Mapped[datetime] = mapped_column(

        DateTime,

        default=datetime.utcnow

    )
