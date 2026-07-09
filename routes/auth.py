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

        session["user_name"] = (

            f"{user.first_name} "

            f"{user.last_name}"

        )

        session["email"] = user.email

        session["user_email"] = user.email

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

    return render_template(

        "profile.html",

        user_name=session.get(

            "user_name"

        ),

        email=session.get(

            "email"

        )

    )
