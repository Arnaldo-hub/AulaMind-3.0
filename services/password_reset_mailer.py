import logging
import smtplib
from email.message import EmailMessage

from flask import current_app

logger = logging.getLogger(__name__)


class PasswordResetMailer:
    @staticmethod
    def send(email, reset_url):
        config = current_app.config
        server = config.get("MAIL_SERVER", "")

        if not server:
            if config.get("DEBUG", False):
                logger.info("PASSWORD RESET DEV URL for %s: %s", email, reset_url)
            return False

        msg = EmailMessage()
        msg["Subject"] = "Recuperación de contraseña — AulaMind"
        msg["From"] = config.get("MAIL_FROM")
        msg["To"] = email
        msg.set_content(
            "Recibimos una solicitud para restablecer tu contraseña.\n\n"
            f"{reset_url}\n\n"
            "Este enlace es temporal. Si no solicitaste este cambio, ignora este mensaje."
        )

        smtp_class = smtplib.SMTP_SSL if config.get("MAIL_USE_SSL", False) else smtplib.SMTP
        with smtp_class(server, config.get("MAIL_PORT", 587), timeout=15) as smtp:
            if config.get("MAIL_USE_TLS", True) and not config.get("MAIL_USE_SSL", False):
                smtp.starttls()
            username = config.get("MAIL_USERNAME", "")
            if username:
                smtp.login(username, config.get("MAIL_PASSWORD", ""))
            smtp.send_message(msg)
        return True
