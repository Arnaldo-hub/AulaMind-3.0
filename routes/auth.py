"""
===========================================================
AulaMind Enterprise 3.0
routes/auth.py
-----------------------------------------------------------

Sistema de Autenticación

• Login
• Registro
• Logout
• Perfil

Autor:
Biotecno Chile
===========================================================
"""

from flask import Blueprint
from flask import render_template
from flask import request
from flask import redirect
from flask import url_for
from flask import flash
from flask import session

from database.session import SessionLocal
from services.auth_service import AuthService
from extensions import limiter

# ==========================================================
# Blueprint
# ==========================================================

auth = Blueprint(
    "auth",
    __name__
)


# ==========================================================
# Login
# ==========================================================

@auth.route("/login", methods=["GET", "POST"])
@limiter.limit("10 per minute", methods=["POST"])
def login():

    if request.method == "GET":

        return render_template("login.html")

    email = request.form.get("email", "").strip().lower()

    password = request.form.get("password", "")

    db = SessionLocal()

    try:

        user = AuthService.login(

            db,

            email,

            password

        )

        if user is None:

            flash(

                "Correo o contraseña incorrectos.",

                "danger"

            )

            return render_template("login.html")

        session.clear()
        session.permanent = True

        session["user_id"] = str(user.id)

        session["role"] = user.role

        session["user_name"] = (

            f"{user.first_name} "

            f"{user.last_name}"

        )

        session["email"] = user.email

        session["user_email"] = user.email
        
        session["school_id"] = user.school_id  # ← FIX: NUEVO

        flash(

            "Bienvenido a AulaMind.",

            "success"

        )

        return redirect(

            url_for("dashboard.home")

        )

    finally:

        db.close()


# ==========================================================
# Registro
# ==========================================================

@auth.route("/register", methods=["GET", "POST"])
@limiter.limit("5 per hour", methods=["POST"])
def register():

    if request.method == "GET":

        return render_template(

            "register.html"

        )

    first_name = request.form.get(

        "first_name",

        ""

    ).strip()

    last_name = request.form.get(

        "last_name",

        ""

    ).strip()

    email = request.form.get(

        "email",

        ""

    ).strip().lower()

    password = request.form.get(

        "password",

        ""

    )

    confirm = request.form.get(

        "confirm_password",

        ""

    )

    if password != confirm:

        flash(

            "Las contraseñas no coinciden.",

            "danger"

        )

        return render_template(

            "register.html"

        )

    db = SessionLocal()

    try:

        AuthService.register_user(

            db,

            first_name,

            last_name,

            email,

            password

        )

        flash(

            "Usuario creado correctamente.",

            "success"

        )

        return redirect(

            url_for("auth.login")

        )

    except Exception as e:

        db.rollback()

        flash(

            str(e),

            "danger"

        )

        return render_template(

            "register.html"

        )

    finally:

        db.close()


# ==========================================================
# Logout
# ==========================================================

@auth.route("/logout")
def logout():

    session.clear()

    flash(

        "Sesión finalizada.",

        "info"

    )

    return redirect(

        url_for("auth.login")

    )


# ==========================================================
# Perfil
# ==========================================================

@auth.route("/profile")
def profile():

    if "user_id" not in session:

        return redirect(

            url_for("auth.login")

        )

    db = SessionLocal()

    try:

        user = AuthService.get_user_by_email(

            db,

            session.get("email")

        )

        if user is None:

            session.clear()

            return redirect(

                url_for("auth.login")

            )

        return render_template(

            "profile.html",

            user=user,

            languages=LANGUAGES,

            timezones=TIMEZONES

        )

    finally:

        db.close()


# ==========================================================
# Actualizar Perfil
# ==========================================================

@auth.route("/profile", methods=["POST"])
def update_profile():

    if "user_id" not in session:

        return redirect(

            url_for("auth.login")

        )

    first_name = request.form.get(

        "first_name", ""

    ).strip()

    last_name = request.form.get(

        "last_name", ""

    ).strip()

    phone = request.form.get(

        "phone", ""

    ).strip() or None

    country = request.form.get(

        "country", ""

    ).strip() or "Chile"

    city = request.form.get(

        "city", ""

    ).strip() or None

    language = request.form.get(

        "language", "es"

    )

    timezone = request.form.get(

        "timezone", "America/Santiago"

    )

    # ------------------------------------------------------
    # Validaciones
    # ------------------------------------------------------

    if not first_name or not last_name:

        flash(

            "Nombre y apellido son obligatorios.",

            "danger"

        )

        return redirect(url_for("auth.profile"))

    if language not in LANGUAGES:

        language = "es"

    if timezone not in TIMEZONES:

        timezone = "America/Santiago"

    db = SessionLocal()

    try:

        user = AuthService.get_user_by_email(

            db,

            session.get("email")

        )

        if user is None:

            session.clear()

            return redirect(

                url_for("auth.login")

            )

        user.first_name = first_name

        user.last_name = last_name

        user.phone = phone

        user.country = country

        user.city = city

        user.language = language

        user.timezone = timezone

        db.commit()

        # --------------------------------------------------
        # Sincronizar nombre en sesión
        # --------------------------------------------------

        session["user_name"] = (

            f"{first_name} {last_name}"

        )

        flash(

            "Perfil actualizado correctamente.",

            "success"

        )

    except Exception:

        db.rollback()

        flash(

            "No se pudo actualizar el perfil.",

            "danger"

        )

    finally:

        db.close()

    return redirect(url_for("auth.profile"))


# ==========================================================
# Cambiar Contraseña
# ==========================================================

@auth.route(
    "/profile/password",
    methods=["POST"]
)
def change_profile_password():

    if "user_id" not in session:

        return redirect(

            url_for("auth.login")

        )

    current_password = request.form.get(

        "current_password", ""

    )

    new_password = request.form.get(

        "new_password", ""

    )

    confirm_password = request.form.get(

        "confirm_password", ""

    )

    # ------------------------------------------------------
    # Validaciones
    # ------------------------------------------------------

    if new_password != confirm_password:

        flash(

            "Las contraseñas nuevas "

            "no coinciden.",

            "danger"

        )

        return redirect(url_for("auth.profile"))

    db = SessionLocal()

    try:

        user = AuthService.get_user_by_email(

            db,

            session.get("email")

        )

        if user is None:

            session.clear()

            return redirect(

                url_for("auth.login")

            )

        if not AuthService.verify_password(

            current_password,

            user.password_hash

        ):

            flash(

                "La contraseña actual "

                "es incorrecta.",

                "danger"

            )

            return redirect(

                url_for("auth.profile")

            )

        try:

            AuthService.change_password(

                db,

                user,

                new_password

            )

        except ValueError as ex:

            flash(str(ex), "danger")

            return redirect(

                url_for("auth.profile")

            )

        flash(

            "Contraseña actualizada "

            "correctamente.",

            "success"

        )

    except Exception:

        db.rollback()

        flash(

            "No se pudo cambiar "

            "la contraseña.",

            "danger"

        )

    finally:

        db.close()

    return redirect(url_for("auth.profile"))


# ==========================================================
# Opciones de Perfil
# ==========================================================

LANGUAGES = {
    "es": "Español",
    "en": "English",
}

TIMEZONES = {
    "America/Santiago": "Santiago (UTC-3/-4)",
    "America/Punta_Arenas": "Punta Arenas (UTC-3)",
    "America/Easter_Island": "Isla de Pascua (UTC-5/-6)",
}
