"""
===========================================================
AulaMind Enterprise 3.0
services/mercadopago_service.py
-----------------------------------------------------------

Integración Mercado Pago — Suscripciones (v3.2)

Modelo elegido: suscripción SIN plan asociado
(POST /preapproval con auto_recurring inline). Es el
camino más flexible para un único precio ($9.990 CLP/mes)
y no requiere formulario de tarjeta propio: el usuario
paga en el checkout hosted de Mercado Pago (init_point).

Reglas de seguridad implementadas (docs oficiales MP):

1. Nunca confiar en el body del webhook ni en el
   redirect del navegador (back_url). Solo se actúa
   sobre el estado CONFIRMADO consultando la API por id.
2. Validación de firma x-signature (HMAC-SHA256) cuando
   MERCADOPAGO_WEBHOOK_SECRET está configurado.
3. Idempotencia vía PaymentEvent (la capa de rutas).

Autor:
Biotecno Chile
===========================================================
"""

import hashlib
import hmac
import logging

import requests

from flask import current_app

logger = logging.getLogger(__name__)

MP_API_BASE = "https://api.mercadopago.com"

# Segundos de espera máximos por llamada a la API
MP_TIMEOUT = 20


class MercadoPagoService:

    # =====================================================
    # Configuración
    # =====================================================

    @staticmethod
    def is_configured():

        config = current_app.config

        return bool(config.get("MERCADOPAGO_ACCESS_TOKEN"))

    @staticmethod
    def _headers():

        token = current_app.config.get(
            "MERCADOPAGO_ACCESS_TOKEN", ""
        )

        return {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }

    # =====================================================
    # Crear suscripción → URL de pago hosted
    # =====================================================

    @staticmethod
    def create_subscription(user_email, user_id):

        """
        Crea la suscripción mensual y devuelve el dict de
        MP (incluye init_point para redirigir al usuario).

        Devuelve None si la API rechaza la creación: la
        capa de rutas muestra mensaje amable y no rompe.
        """

        config = current_app.config

        price = config.get("PRO_MONTHLY_PRICE_CLP", 9990)
        back_url = config.get(
            "MERCADOPAGO_SUCCESS_URL",
            "https://www.aulamind.cl/payments/return",
        )

        payload = {
            "reason": (
                f"AulaMind Plan Pro — ${price:,} CLP/mes"
                .replace(",", ".")
            ),
            # Llave de unión con nuestro usuario: llega de
            # vuelta en cada webhook de la suscripción.
            "external_reference": str(user_id),
            "payer_email": user_email,
            "auto_recurring": {
                "frequency": 1,
                "frequency_type": "months",
                "transaction_amount": price,
                "currency_id": "CLP",
            },
            "back_url": back_url,
        }

        try:

            response = requests.post(
                f"{MP_API_BASE}/preapproval",
                json=payload,
                headers=MercadoPagoService._headers(),
                timeout=MP_TIMEOUT,
            )

            if response.status_code not in (200, 201):

                logger.error(
                    "MP create_subscription rechazado "
                    "(%s): %s",
                    response.status_code,
                    response.text[:300],
                )

                return None

            return response.json()

        except requests.RequestException:

            logger.exception("MP create_subscription: error de red")

            return None

    # =====================================================
    # Consultas por id (la única verdad)
    # =====================================================

    @staticmethod
    def get_preapproval(preapproval_id):

        """Estado real de la suscripción (authorized /
        paused / cancelled / pending)."""

        return MercadoPagoService._get(
            f"/preapproval/{preapproval_id}"
        )

    @staticmethod
    def get_authorized_payment(payment_id):

        """Estado real de un cobro recurrente (factura).
        Trae preapproval_id y external_reference."""

        return MercadoPagoService._get(
            f"/authorized_payments/{payment_id}"
        )

    @staticmethod
    def _get(path):

        try:

            response = requests.get(
                f"{MP_API_BASE}{path}",
                headers=MercadoPagoService._headers(),
                timeout=MP_TIMEOUT,
            )

            if response.status_code != 200:

                logger.error(
                    "MP GET %s → %s: %s",
                    path,
                    response.status_code,
                    response.text[:300],
                )

                return None

            return response.json()

        except requests.RequestException:

            logger.exception("MP GET %s: error de red", path)

            return None

    # =====================================================
    # Firma de webhooks (HMAC-SHA256)
    # =====================================================

    @staticmethod
    def verify_signature(x_signature, x_request_id, data_id):

        """
        Valida que el POST venga realmente de Mercado Pago.

        Manifiesto exacto (docs oficiales):
            id:<data.id>;request-id:<x-request-id>;ts:<ts>;

        Devuelve True si no hay secreto configurado (modo
        permisivo con warning: la consulta por id sigue
        siendo la barrera real, pero el secreto debe
        configurarse en producción).
        """

        secret = current_app.config.get(
            "MERCADOPAGO_WEBHOOK_SECRET", ""
        )

        if not secret:

            logger.warning(
                "MERCADOPAGO_WEBHOOK_SECRET no configurado: "
                "webhook aceptado sin validar firma"
            )

            return True

        if not x_signature or not data_id:

            return False

        parts = {}

        for chunk in x_signature.split(","):

            key, _, value = chunk.strip().partition("=")

            if key:
                parts[key] = value

        ts = parts.get("ts")
        received_hash = parts.get("v1")

        if not ts or not received_hash:

            return False

        manifest = (
            f"id:{data_id};"
            f"request-id:{x_request_id or ''};"
            f"ts:{ts};"
        )

        expected_hash = hmac.new(
            secret.encode("utf-8"),
            manifest.encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()

        return hmac.compare_digest(
            expected_hash.lower(),
            received_hash.lower(),
        )
