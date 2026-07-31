"""
===========================================================
AulaMind Enterprise 3.0
routes/dashboard.py
-----------------------------------------------------------

Dashboard principal del sistema.

Autor:
Biotecno Chile
AulaMind Enterprise

===========================================================
"""

from flask import Blueprint
from flask import render_template
from flask import current_app
from flask import session
from services.persistence_service import persistence_service


# ==========================================================
# Blueprint
# ==========================================================

dashboard = Blueprint(
    "dashboard",
    __name__
)


# ==========================================================
# Dashboard Principal
# ==========================================================

@dashboard.route("/dashboard/")
def home():
    """
    Página principal de AulaMind.

    v3.1: se movió de "/" a "/dashboard/" para que la raíz
    muestre la landing pública. Las plantillas usan
    url_for('dashboard.home'), así que no hay enlaces rotos.
    """

    return render_template(

        "dashboard.html",

        app_name=current_app.config["APP_NAME"],

        version=current_app.config["APP_VERSION"],

        company=current_app.config["COMPANY"],

        stats=persistence_service.dashboard_stats(session.get("user_id"))
        if session.get("user_id") else {
            "planning_count": 0,
            "evaluation_count": 0,
            "guide_count": 0,
            "rubric_count": 0,
            "total_documents": 0,
            "time_saved_hours": 0,
        }

    )


# ==========================================================
# Health Check
# ==========================================================

@dashboard.route("/health")
def health():
    """
    Verificación rápida del estado del sistema.
    """

    return {

        "status": "ok",

        "application": current_app.config["APP_NAME"],

        "version": current_app.config["APP_VERSION"]

    }


# ==========================================================
# About
# ==========================================================

@dashboard.route("/about")
def about():
    """
    Información básica de la aplicación.
    """

    return {

        "application": current_app.config["APP_NAME"],

        "version": current_app.config["APP_VERSION"],

        "company": current_app.config["COMPANY"],

        "country": current_app.config["COUNTRY"],

        "language": current_app.config["DEFAULT_LANGUAGE"]

    }


# ==========================================================
# Ping
# ==========================================================

@dashboard.route("/ping")
def ping():

    return {

        "message": "pong"

    }