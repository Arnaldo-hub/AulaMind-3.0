"""
===========================================================
AulaMind Enterprise 3.0
services/payment_mailer.py
-----------------------------------------------------------

Envío de correos transaccionales de pagos.

Autor:
Biotecno Chile
===========================================================
"""

import logging

from flask import current_app

logger = logging.getLogger(__name__)


class PaymentMailer:

    """
    Envío de correos transaccionales de pagos.
    """

    # =====================================================
    # Envío genérico
    # =====================================================

    @staticmethod
    def _send(to_email, subject, body):

        """
        Envía un correo simple (texto plano).

        En producción se puede reemplazar por SendGrid,
        Resend, AWS SES, etc.
        """

        try:

            import smtplib
            from email.mime.text import MIMEText

            config = current_app.config

            smtp_host = config.get("SMTP_HOST", "")
            smtp_port = config.get("SMTP_PORT", 587)
            smtp_user = config.get("SMTP_USER", "")
            smtp_pass = config.get("SMTP_PASSWORD", "")
            sender = config.get("SMTP_FROM", smtp_user)

            if not smtp_host or not smtp_user:
                logger.warning(
                    "PaymentMailer: SMTP no configurado, "
                    "correo simulado: to=%s subject=%s",
                    to_email,
                    subject,
                )
                return True

            msg = MIMEText(body, "plain", "utf-8")
            msg["Subject"] = subject
            msg["From"] = sender
            msg["To"] = to_email

            with smtplib.SMTP(smtp_host, smtp_port) as server:
                server.starttls()
                server.login(smtp_user, smtp_pass)
                server.sendmail(sender, [to_email], msg.as_string())

            logger.info("PaymentMailer: correo enviado a %s", to_email)

            return True

        except Exception:

            logger.exception("PaymentMailer: error enviando correo")

            return False

    # =====================================================
    # Correos específicos
    # =====================================================

    @staticmethod
    def send_payment_success(user_email, user_name, amount):

        """
        Notifica al usuario que su pago fue exitoso.
        """

        subject = (
            "¡Gracias por suscribirte a AulaMind Pro!"
        )

        body = (
            f"Hola {user_name or 'docente'},\n\n"
            f"Tu suscripción a AulaMind Pro fue confirmada.\n"
            f"Monto: ${amount:,} CLP\n"
            f"Periodo: 30 días\n\n"
            f"Ya puedes generar documentos sin límite.\n"
            f"https://www.aulamind.cl/dashboard\n\n"
            f"AulaMind Enterprise 3.0"
        )

        return PaymentMailer._send(user_email, subject, body)

    @staticmethod
    def send_payment_failed(user_email, user_name, reason):

        """
        Notifica al usuario que su pago falló.
        """

        subject = "Tu pago en AulaMind no pudo procesarse"

        body = (
            f"Hola {user_name or 'docente'},\n\n"
            f"Tu intento de pago no pudo completarse: {reason}\n\n"
            f"Puedes intentar nuevamente desde:"
            f" https://www.aulamind.cl/plan\n\n"
            f"Si necesitas ayuda, contáctanos.\n\n"
            f"AulaMind Enterprise 3.0"
        )

        return PaymentMailer._send(user_email, subject, body)

    # =====================================================
    # Notificación al admin cuando un usuario paga
    # =====================================================

    @staticmethod
    def send_admin_notification(user_email, user_name, amount):
        """
        Envía email al administrador cuando un usuario
        completa un pago en MercadoPago.
        """

        config = current_app.config

        admin_email = config.get("ADMIN_EMAIL", "")
        if not admin_email:
            logger.warning(
                "PaymentMailer: ADMIN_EMAIL no configurado, "
                "notificación omitida"
            )
            return False

        subject = f"💰 Nuevo pago en AulaMind: {user_email}"

        body = (
            f"Hola,\n\n"
            f"Un usuario acaba de pagar en AulaMind:\n\n"
            f"  Email: {user_email}\n"
            f"  Nombre: {user_name or 'No disponible'}\n"
            f"  Monto: ${amount:,} CLP\n\n"
            f"Recuerda activar su plan desde el Panel Comercial si "
            f"no se activó automáticamente.\n\n"
            f"Panel: https://www.aulamind.cl/admin/comercial\n\n"
            f"AulaMind Enterprise 3.0"
        )

        return PaymentMailer._send(admin_email, subject, body)
