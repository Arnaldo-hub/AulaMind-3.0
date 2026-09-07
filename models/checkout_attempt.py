"""
===========================================================
AulaMind Enterprise 3.0
models/checkout_attempt.py
-----------------------------------------------------------

Registro de intentos de checkout en Mercado Pago.
===========================================================
"""

from sqlalchemy import Column, Integer, String, DateTime, Text
from sqlalchemy.sql import func
from database.base import Base


class CheckoutAttempt(Base):
    """
    Intentos de checkout (suscripción Pro) para
    rastreo y soporte.
    """
    __tablename__ = "checkout_attempts"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String(36), nullable=False, index=True)
    plan_name = Column(String(50), nullable=False)
    status = Column(String(20), nullable=False, default="pending")
    mp_preapproval_id = Column(String(100), nullable=True)
    raw_response = Column(Text, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())