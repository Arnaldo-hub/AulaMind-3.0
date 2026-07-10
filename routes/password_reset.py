import logging
import re
from flask import Blueprint, flash, redirect, render_template, request, url_for
from database.session import SessionLocal
from extensions import limiter
from services.auth_service import AuthService
from services.password_reset_mailer import PasswordResetMailer
from services.password_reset_service import PasswordResetService

logger = logging.getLogger(__name__)

password_reset = Blueprint("password_reset", __name__)
NEUTRAL_MESSAGE = "Si existe una cuenta asociada a ese correo, recibirás instrucciones para continuar."

def _policy_error(password):
    if len(password) < 10: return "La contraseña debe tener al menos 10 caracteres."
    if not re.search(r"[A-Z]", password): return "La contraseña debe incluir una letra mayúscula."
    if not re.search(r"[a-z]", password): return "La contraseña debe incluir una letra minúscula."
    if not re.search(r"\d", password): return "La contraseña debe incluir un número."
    return None

@password_reset.route("/forgot-password", methods=["GET", "POST"])
@limiter.limit("5 per hour", methods=["POST"])
def forgot_password():
    if request.method == "GET":
        return render_template("forgot_password.html")
    email = request.form.get("email", "").strip().lower()
    db = SessionLocal()
    try:
        user = AuthService.get_user_by_email(db, email)
        if user is not None and user.is_active:
            token = PasswordResetService.generate_token(user)
            reset_url = url_for("password_reset.reset_password", token=token, _external=True)
            try:
                PasswordResetMailer.send(user.email, reset_url)
            except Exception:
                # La respuesta al usuario sigue siendo neutral, pero el error queda visible en logs.
                logger.exception("No fue posible enviar el correo de recuperación")
        flash(NEUTRAL_MESSAGE, "info")
        return render_template("forgot_password.html")
    finally:
        db.close()

@password_reset.route("/reset-password/<token>", methods=["GET", "POST"])
@limiter.limit("10 per hour", methods=["POST"])
def reset_password(token):
    db = SessionLocal()
    try:
        user = PasswordResetService.verify_token(token, db)
        if user is None:
            flash("El enlace no es válido o ha expirado.", "danger")
            return redirect(url_for("password_reset.forgot_password"))
        if request.method == "GET":
            return render_template("reset_password.html")
        password = request.form.get("password", "")
        confirm = request.form.get("confirm_password", "")
        if password != confirm:
            flash("Las contraseñas no coinciden.", "danger")
            return render_template("reset_password.html")
        error = _policy_error(password)
        if error:
            flash(error, "danger")
            return render_template("reset_password.html")
        AuthService.change_password(db, user, password)
        flash("Contraseña actualizada correctamente. Ya puedes iniciar sesión.", "success")
        return redirect(url_for("auth.login"))
    finally:
        db.close()
