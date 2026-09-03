"""
===========================================================
AulaMind Enterprise 3.0
routes/payments.py
-----------------------------------------------------------

Pagos con Mercado Pago — Suscripciones (v3.2)

Flujo:

1. GET  /payments/checkout  → crea la suscripción en MP
   y redirige al checkout hosted (init_point). El usuario
   paga con tarjeta en Mercado Pago.
2. GET  /payments/return    → back_url: página "estamos
   confirmando" mientras llega el webhook.
3. POST /payments/webhook   → notificaciones de MP. Es la
   ÚNICA vía que activa/extiende planes. Nunca se confía
   en el body ni en el redirect: se consulta el recurso
   por id a la API y se actúa sobre el estado confirmado.

Eventos manejados:

- subscription_preapproval (authorized) → activa el plan
  de inmediato (silencioso, sin correo).
- subscription_authorized_payment (approved) → activa/
  renueva el plan y envía confirmación por correo.
- subscription_authorized_payment (rechazado) → correo
  de dunning (el acceso expira solo si no se regulariza).

Regla de oro de renovación: Entitlements.activate_paid
REINICIA la ventana a +31 días desde el cobro, no acumula
— un webhook duplicado nunca regala días. La tabla
payment_events asegura idempotencia y deja auditoría.

Autor:
Biotecno Chile
===========================================================
"""

import logging

from flask import Blueprint
from flask import current_app
from flask import jsonify
from flask import redirect
from flask import render_template
from flask import request
from flask import session
from flask import url_for

from database.session import SessionLocal
from models.payment_event import PaymentEvent
from models.user import User
from services.entitlements import Entitlements
from services.mercadopago_service import MercadoPagoService
from services.payment_mailer import PaymentMailer

logger = logging.getLogger(__name__)

# Días de acceso por cobro mensual confirmado
# (30 del mes + 1 de gracia por desfase del webhook)
PAID_PERIOD_DAYS = 31

# ==========================================================
# Blueprint
# ==========================================================

payments = Blueprint(
    "payments",
    __name__,
    url_prefix="/payments"
)


# ==========================================================
# Checkout: crear suscripción y enviar al usuario a MP
# ==========================================================

@payments.route("/checkout")
@login_required
def checkout():
    """
    v3.2: Redirige al Plan Link de Mercado Pago.
    El usuario paga en MP y luego MP redirige a /payments/return.
    """
    # URL de retorno después del pago en MP
    return_url = url_for(
        "payments.return_page",
        _external=True,
        _scheme="https"
    )

    # Plan Link de Mercado Pago para AulaMind Pro $9.990/mes
    plan_link = "https://mpago.la/2QapPYJ"

    # Redirigir al Plan Link de MP con URL de retorno
    redirect_url = f"{plan_link}?back_url={return_url}"
    
    return redirect(redirect_url)


# ==========================================================
# Back URL: el usuario vuelve desde Mercado Pago
# ==========================================================

@payments.route("/return", methods=["GET"])
def return_page():

    user_id = session.get("user_id")

    if not user_id:
        return redirect(url_for("auth.login"))

    plan = Entitlements.get_status(user_id)

    return render_template(
        "payments_return.html",
        plan=plan,
    )


# ==========================================================
# Webhook: la única fuente de verdad
# ==========================================================

@payments.route("/webhook", methods=["POST"])
def webhook():

    # MP envía JSON (v1: {"type", "data": {"id"}}); el
    # formato legado usa query string (?topic=&id=).
    body = request.get_json(silent=True) or {}

    event_type = (
        body.get("type")
        or request.args.get("topic")
        or ""
    )

    data_id = (
        request.args.get("data.id")
        or (body.get("data") or {}).get("id")
        or request.args.get("id")
        or ""
    )

    data_id = str(data_id)

    # 1) Firma: confirma que el POST viene de Mercado Pago
    if not MercadoPagoService.verify_signature(
        x_signature=request.headers.get("x-signature", ""),
        x_request_id=request.headers.get("x-request-id", ""),
        data_id=data_id,
    ):

        logger.warning(
            "Webhook MP con firma inválida (data.id=%s)",
            data_id,
        )

        return jsonify({"error": "invalid_signature"}), 401

    if not event_type or not data_id:
        return jsonify({"status": "ignored"}), 200

    # 2) Procesar (siempre 200 para que MP no reintente
    #    indefinidamente; los errores quedan en log)
    try:

        action = process_mp_webhook(event_type, data_id)

    except Exception:

        logger.exception(
            "Webhook MP falló procesando %s %s",
            event_type,
            data_id,
        )

        action = "error"

    return jsonify({"status": action}), 200


# ==========================================================
# Procesamiento de eventos (separado para poder probarlo
# y para mantener el handler delgado)
# ==========================================================

def process_mp_webhook(event_type, resource_id):

    event_key = f"{event_type}:{resource_id}"

    db = SessionLocal()

    try:

        # ----------------------------------------------
        # Idempotencia: cada evento se procesa una vez
        # ----------------------------------------------

        already = db.query(PaymentEvent).filter(
            PaymentEvent.provider == "mercadopago",
            PaymentEvent.event_key == event_key,
        ).first()

        if already is not None:
            return "duplicate"

        action = "ignored"
        user_id = None
        detail = ""

        # ----------------------------------------------
        # Ciclo de vida de la suscripción
        # ----------------------------------------------

        if event_type == "subscription_preapproval":

            preapproval = MercadoPagoService.get_preapproval(
                resource_id
            )

            if preapproval:

                status = preapproval.get("status", "")
                user_id = preapproval.get("external_reference")
                detail = f"status={status}"

                if status == "authorized" and user_id:

                    # Acceso inmediato al suscribirse. El
                    # correo lo envía el evento de cobro.
                    Entitlements.activate_paid(
                        db,
                        user_id,
                        days=PAID_PERIOD_DAYS,
                        source="mercadopago",
                    )

                    action = "activated"

                else:
                    # paused / cancelled / pending: el
                    # acceso expira solo al cumplirse el
                    # período ya pagado. Solo dejamos
                    # registro.
                    action = "noted"

        # ----------------------------------------------
        # Cobro recurrente (cada ciclo mensual)
        # ----------------------------------------------

        elif event_type == "subscription_authorized_payment":

            payment = (
                MercadoPagoService.get_authorized_payment(
                    resource_id
                )
            )

            if payment:

                status = payment.get("status", "")
                detail = f"status={status}"

                # Resolver nuestro usuario: primero la
                # referencia directa; si no viene, la de
                # la suscripción madre (llave robusta).
                user_id = payment.get("external_reference")

                if not user_id and payment.get("preapproval_id"):

                    parent = (
                        MercadoPagoService.get_preapproval(
                            payment["preapproval_id"]
                        )
                    )

                    if parent:
                        user_id = parent.get(
                            "external_reference"
                        )

                if user_id:

                    if status == "approved":

                        Entitlements.activate_paid(
                            db,
                            user_id,
                            days=PAID_PERIOD_DAYS,
                            source="mercadopago",
                        )

                        _notify(
                            db,
                            user_id,
                            PaymentMailer.send_activated,
                            current_app.config.get(
                                "PRO_MONTHLY_PRICE_CLP", 9990
                            ),
                        )

                        action = "activated"

                    else:

                        # Cobro rechazado: dunning amable.
                        # MP reintenta solo; el acceso
                        # expira por tiempo si no paga.
                        _notify(
                            db,
                            user_id,
                            PaymentMailer.send_payment_failed,
                        )

                        action = "payment_failed"

        # ----------------------------------------------
        # Auditoría
        # ----------------------------------------------

        db.add(PaymentEvent(
            provider="mercadopago",
            event_key=event_key,
            user_id=str(user_id) if user_id else None,
            action=action,
            detail=detail[:490],
        ))

        db.commit()

        return action

    finally:

        db.close()


# ==========================================================
# Helper: correo al usuario sin tumbar el webhook
# ==========================================================

def _notify(db, user_id, send_fn, *args):

    try:

        user = db.query(User).filter(
            User.id == str(user_id)
        ).first()

        if user and user.email:

            send_fn(
                user.email,
                user.first_name or "docente",
                *args,
            )

    except Exception:

        logger.exception(
            "No se pudo notificar por correo al usuario %s",
            user_id,
        )
