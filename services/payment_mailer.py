"""
===========================================================
AulaMind Enterprise 3.0
services/payment_mailer.py
-----------------------------------------------------------

Correos del flujo de pagos (v3.2)

- send_activated:      plan Pro activado/renovado
- send_payment_failed: un cobro mensual fue rechazado
                       (dunning amable: invita a actualizar
                       el medio de pago antes de perder
                       acceso)

Sigue el mismo patrón que PasswordResetMailer: smtplib
directo con la configuración MAIL_* de la app. Nunca
tumba el webhook: cualquier falla de envío queda en log
y devuelve False.

Autor:
Biotecno Chile
===========================================================
"""

import logging
import smtplib
from email.message import EmailMessage

from flask import current_app

logger = logging.getLogger(__name__)


class PaymentMailer:

    # =====================================================
    # Transporte compartido
    # =====================================================

    @staticmethod
    def _send(email, subject, body):

        config = current_app.config
        server = config.get("MAIL_SERVER", "")

        if not server:

            logger.warning(
                "PaymentMailer sin MAIL_SERVER: correo '%s' "
                "para %s omitido",
                subject,
                email,
            )

            return False

        try:

            msg = EmailMessage()
            msg["Subject"] = subject
            msg["From"] = config.get("MAIL_FROM")
            msg["To"] = email
            msg.set_content(body)

            smtp_class = (
                smtplib.SMTP_SSL
                if config.get("MAIL_USE_SSL", False)
                else smtplib.SMTP
            )

            with smtp_class(
                server,
                config.get("MAIL_PORT", 587),
                timeout=15,
            ) as smtp:

                if config.get(
                    "MAIL_USE_TLS", True
                ) and not config.get("MAIL_USE_SSL", False):

                    smtp.starttls()

                username = config.get("MAIL_USERNAME", "")

                if username:
                    smtp.login(
                        username,
                        config.get("MAIL_PASSWORD", ""),
                    )

                smtp.send_message(msg)

            return True

        except Exception:

            logger.exception(
                "PaymentMailer: no se pudo enviar '%s' a %s",
                subject,
                email,
            )

            return False

    # =====================================================
    # Plan activado / renovado
    # =====================================================

    @staticmethod
    def send_activated(email, name, price_clp):

        price = f"{int(price_clp):,}".replace(",", ".")

        return PaymentMailer._send(
            email,
            "Tu Plan Pro está activo — AulaMind",
            (
                f"Hola {name}:\n\n"
                "Tu suscripción a AulaMind Plan Pro quedó "
                "activa. Ya puedes generar planificaciones, "
                "evaluaciones, guías, rúbricas y PIE sin "
                "límite práctico.\n\n"
                f"Valor mensual: ${price} CLP, cobrado "
                "automáticamente por Mercado Pago. Puedes "
                "cancelar cuando quieras desde tu cuenta de "
                "Mercado Pago, sin permanencia.\n\n"
                "Gracias por confiar en AulaMind.\n"
                "— Equipo AulaMind · aulamind.cl"
            ),
        )

    # =====================================================
    # Cobro rechazado (renovación fallida)
    # =====================================================

    @staticmethod
    def send_payment_failed(email, name):

        return PaymentMailer._send(
            email,
            "No pudimos cobrar tu suscripción — AulaMind",
            (
                f"Hola {name}:\n\n"
                "Mercado Pago rechazó el cobro mensual de tu "
                "Plan Pro. No te preocupes: tu acceso sigue "
                "activo mientras se reintenta el pago.\n\n"
                "Para no perder acceso, actualiza tu tarjeta "
                "desde tu cuenta de Mercado Pago (sección "
                "Suscripciones).\n\n"
                "Si necesitas ayuda, responde este correo o "
                "escríbenos a contacto@aulamind.cl.\n\n"
                "— Equipo AulaMind · aulamind.cl"
            ),
        )
