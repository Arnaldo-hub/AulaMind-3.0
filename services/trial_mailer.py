"""
===========================================================
AulaMind Enterprise 3.0
services/trial_mailer.py
-----------------------------------------------------------

Correos automáticos del ciclo de trial:

1. Bienvenida (día 0)  — al registrarse
2. Aviso (queda 1 día) — día 2
3. Expiración (día 3)  — trial terminado

Usa el mismo patrón SMTP que PasswordResetMailer.
Si MAIL_SERVER no está configurado, no envía y
retorna False (la plataforma sigue funcionando).

Autor:
Biotecno Chile
===========================================================
"""

import logging
import smtplib
from email.message import EmailMessage

from flask import current_app

logger = logging.getLogger(__name__)


class TrialMailer:

    # --------------------------------------------------
    # Envío base
    # --------------------------------------------------

    @staticmethod
    def _send(email, subject, body):

        config = current_app.config
        server = config.get("MAIL_SERVER", "")

        if not server:
            logger.info(
                "MAIL no configurado — correo omitido para %s: %s",
                email, subject
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
                timeout=15
            ) as smtp:

                if config.get("MAIL_USE_TLS", True) and not config.get(
                    "MAIL_USE_SSL", False
                ):
                    smtp.starttls()

                username = config.get("MAIL_USERNAME", "")

                if username:
                    smtp.login(
                        username,
                        config.get("MAIL_PASSWORD", "")
                    )

                smtp.send_message(msg)

            return True

        except Exception:

            logger.exception(
                "Error enviando correo de trial a %s", email
            )
            return False

    # --------------------------------------------------
    # 1. Bienvenida (día 0)
    # --------------------------------------------------

    @staticmethod
    def send_welcome(email, name, trial_days, max_generations):

        return TrialMailer._send(
            email,
            f"Bienvenido a AulaMind — tu trial de {trial_days} días está activo",
            (
                f"Hola {name}:\n\n"
                f"Tu cuenta AulaMind está lista. Tienes {trial_days} días "
                f"de prueba gratuita con hasta {max_generations} documentos "
                f"con Inteligencia Artificial, alineados al Currículum "
                f"Nacional MINEDUC.\n\n"
                "Te recomendamos partir ahora: genera tu primera "
                "planificación en 2 minutos en https://www.aulamind.cl\n\n"
                "Al finalizar el trial puedes suscribirte para seguir "
                "generando sin límites.\n\n"
                "Equipo AulaMind — Biotecno Chile"
            )
        )

    # --------------------------------------------------
    # 2. Aviso: queda 1 día (día 2)
    # --------------------------------------------------

    @staticmethod
    def send_warning(email, name, remaining_generations):

        return TrialMailer._send(
            email,
            "Te queda 1 día de trial en AulaMind",
            (
                f"Hola {name}:\n\n"
                "Tu período de prueba termina mañana. "
                f"Te quedan {remaining_generations} generaciones "
                "disponibles.\n\n"
                "Para no perder el acceso a tus documentos ni al "
                "generador, suscríbete en https://www.aulamind.cl/plan\n\n"
                "Equipo AulaMind — Biotecno Chile"
            )
        )

    # --------------------------------------------------
    # 3. Expiración (día 3)
    # --------------------------------------------------

    @staticmethod
    def send_expired(email, name):

        return TrialMailer._send(
            email,
            "Tu trial de AulaMind ha terminado",
            (
                f"Hola {name}:\n\n"
                "Tu período de prueba de 3 días terminó. Tus documentos "
                "siguen guardados y disponibles cuando lo necesites.\n\n"
                "Para seguir generando planificaciones, evaluaciones, "
                "guías, rúbricas y PIE con IA, suscríbete en "
                "https://www.aulamind.cl/plan\n\n"
                "Equipo AulaMind — Biotecno Chile"
            )
        )
