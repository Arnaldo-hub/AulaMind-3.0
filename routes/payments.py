"""
===========================================================
AulaMind Enterprise 3.0
routes/payments.py
-----------------------------------------------------------

Integración con Mercado Pago (v3.2)

Autor:
Biotecno Chile
===========================================================
"""

import logging

from flask import Blueprint
from flask import jsonify
from flask import redirect
from flask import render_template
from flask import request
from flask import session
from flask import url_for

from database.session import SessionLocal
from models.checkout_attempt import CheckoutAttempt
from models.payment_event import PaymentEvent
from models.user import User
from services.entitlements import Entitlements
from services.mercadopago_service import MercadoPagoService
from services.payment_mailer import PaymentMailer

logger = logging.getLogger(__name__)

# ==========================================================
# Blueprint
# ==========================================================

payments = Blueprint(
    "payments",
    __name__
)

# ==========================================================
# Configuración
# ==========================================================

PAID_PERIOD_DAYS = 30


# ==========================================================
# Checkout: crea la suscripción en MP y redirige
# ==========================================================

@payments.route("/checkout")
@login_required
def checkout():
    """
    v3.2: Crea suscripción en MP vía API y redirige al checkout hosted.
    El usuario paga en MP y luego MP redirige a /payments/return.
    El webhook /payments/webhook activa el plan automáticamente.
    """
    user_id = session.get("user_id")
    if not user_id:
        return redirect(url_for("auth.login"))

    db = SessionLocal()
    try:
        user = db.query(User).filter(User.id == str(user_id)).first()
        if not user or not user.email:
            logger.error("Checkout MP: usuario %s sin email", user_id)
            return render_template(
                "payments_return.html",
                plan={"status": "error"},
                error="No encontramos tu correo. Contacta soporte."
            ), 400

        # Crear suscripción en MercadoPago vía API
        mp_data = MercadoPagoService.create_subscription(
            user_email=user.email,
            user_id=user.id,
        )

        if mp_data and mp_data.get("init_point"):
            # Guardar el preapproval_id en sesión para poder
            # verificar el estado al volver de MP (respaldo
            # si el webhook no llega).
            session["mp_preapproval_id"] = mp_data.get("id")
            session.modified = True

            # Registrar intento de checkout para el panel
            # de activaciones pendientes.
            db2 = SessionLocal()
            try:
                db2.add(CheckoutAttempt(
                    user_id=str(user_id),
                    mp_preapproval_id=mp_data.get("id"),
                ))
                db2.commit()
            except Exception:
                logger.exception("Error guardando checkout attempt")
            finally:
                db2.close()

            # Redirigir al checkout hosted de MP
            return redirect(mp_data["init_point"])

        # Fallback: si la API falla o no devuelve init_point,
        # usar el Plan Link de MP como respaldo.
        logger.warning(
            "Checkout MP: API falló para user %s, usando Plan Link fallback",
            user_id,
        )

        plan_link = "https://mpago.la/2QapPYJ"
        return_url = url_for(
            "payments.return_page",
            _external=True,
            _scheme="https",
        )
        redirect_url = f"{plan_link}?back_url={return_url}"
        return redirect(redirect_url)

    finally:
        db.close()


# ==========================================================
# Webhook: Mercado Pago notifica eventos de pago
# ==========================================================

@payments.route("/webhook", methods=["GET", "POST"])
def webhook():

    # Mercado Pago envía GET al configurar el webhook (challenge).
    # Respondemos 200 para que MP acepte la URL.
    if request.method == "GET":
        return jsonify({"status": "ok"}), 200

    # MP envía JSON (v1: {"type", "data": {"id"}}); el
    # formato legado usa query string (?topic=&id=).
    body = request.get_json(silent=True) or {}

    event_type = body.get("type", "")
    resource_id = body.get("data", {}).get("id")

    # Si no hay JSON, intentar query string (legacy)
    if not resource_id:
        resource_id = request.args.get("id")
        event_type = request.args.get("topic", "")

    if not resource_id:
        logger.warning("Webhook MP: falta resource_id")
        return jsonify({"status": "ignored"}), 200

    # Verificar firma del webhook (v3.2)
    if not MercadoPagoService.verify_webhook_signature(
        request.get_data(as_text=True),
        request.headers.get("x-signature", ""),
        request.headers.get("x-request-id", ""),
    ):
        logger.warning("Webhook MP con firma inválida")
        return jsonify({"status": "ignored"}), 200

    # Guardar evento (idempotencia + auditoría)
    db = SessionLocal()
    try:
        existing = db.query(PaymentEvent).filter(
            PaymentEvent.provider == "mercadopago",
            PaymentEvent.provider_event_id == str(resource_id),
        ).first()

        if existing:
            return jsonify({"status": "duplicate"}), 200

        event = PaymentEvent(
            provider="mercadopago",
            provider_event_id=str(resource_id),
            action=event_type,
            detail=f"type={event_type} id={resource_id}",
        )
        db.add(event)
        db.commit()
    finally:
        db.close()

    # =====================================================
    # Procesar evento
    # =====================================================

    if event_type == "subscription_preapproval":

        preapproval = MercadoPagoService.get_preapproval(
            resource_id
        )

        if preapproval:

            status = preapproval.get("status", "")
            # El external_reference ahora tiene formato
            # "user_id:uuid". Extraemos solo el user_id.
            raw_ref = preapproval.get("external_reference", "")
            user_id = raw_ref.split(":")[0] if raw_ref else None
            detail = f"status={status} ref={raw_ref[:50]}"

            if status == "authorized" and user_id:

                db = SessionLocal()
                try:

                    user = db.query(User).filter(
                        User.id == str(user_id)
                    ).first()

                    if user:

                        Entitlements.activate_paid(
                            db,
                            user.id,
                            days=PAID_PERIOD_DAYS,
                            source="mercadopago",
                        )

                        # Notificar al admin del nuevo pago
                        PaymentMailer.send_admin_notification(
                            user_email=user.email,
                            user_name=user.name,
                            amount=9990,
                        )

                        logger.info(
                            "Webhook MP: Plan activado para user %s",
                            user_id,
                        )

                finally:
                    db.close()

    elif event_type == "subscription_authorized_payment":

        payment = MercadoPagoService.get_authorized_payment(
            resource_id
        )

        if payment:

            status = payment.get("status", "")
            detail = f"status={status}"

            if status == "approved":

                # Resolver nuestro usuario: primero la
                # referencia directa; si no viene, la de
                # la suscripción madre (llave robusta).
                raw_ref = payment.get("external_reference", "")
                user_id = raw_ref.split(":")[0] if raw_ref else None

                if not user_id and payment.get("preapproval_id"):

                    parent = MercadoPagoService.get_preapproval(
                        payment["preapproval_id"]
                    )

                    if parent:
                        raw_ref = parent.get(
                            "external_reference", ""
                        )
                        user_id = raw_ref.split(":")[0] if raw_ref else None

                if user_id:

                    db = SessionLocal()
                    try:

                        user = db.query(User).filter(
                            User.id == str(user_id)
                        ).first()

                        if user:

                            Entitlements.activate_paid(
                                db,
                                user.id,
                                days=PAID_PERIOD_DAYS,
                                source="mercadopago",
                            )

                            logger.info(
                                "Webhook MP: Plan renovado "
                                "para user %s",
                                user_id,
                            )

                    finally:
                        db.close()

    logger.info("Webhook MP procesado: %s", detail)

    return jsonify({"status": "ok"}), 200


# ==========================================================
# Página de retorno después del pago en MP
# ==========================================================

@payments.route("/return", methods=["GET"])
def return_page():

    user_id = session.get("user_id")

    if not user_id:
        return redirect(url_for("auth.login"))

    # Respaldo: si el webhook no llegó, consultamos directamente
    # a MP el estado de la suscripción recién creada.
    preapproval_id = session.pop("mp_preapproval_id", None)

    if preapproval_id:
        try:
            preapproval = MercadoPagoService.get_preapproval(
                preapproval_id
            )
            if preapproval and preapproval.get("status") == "authorized":
                # Extraer user_id del external_reference (formato user_id:uuid)
                raw_ref = preapproval.get("external_reference", "")
                ref_user_id = raw_ref.split(":")[0] if raw_ref else None

                if ref_user_id and str(ref_user_id) == str(user_id):
                    db = SessionLocal()
                    try:
                        Entitlements.activate_paid(
                            db,
                            user_id,
                            days=PAID_PERIOD_DAYS,
                            source="mercadopago_return",
                        )
                        logger.info(
                            "Plan activado vía return_page para user %s",
                            user_id,
                        )
                    finally:
                        db.close()
        except Exception:
            logger.exception(
                "Error consultando MP en return_page for user %s",
                user_id,
            )

    plan = Entitlements.get_status(user_id)

    return render_template(
        "payments_return.html",
        plan=plan,
    )
