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

from datetime import datetime

from flask import Blueprint
from flask import render_template
from flask import current_app
from flask import session
from flask import url_for
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

    user_id = session.get("user_id")

    stats = (
        persistence_service.dashboard_stats(user_id)
        if user_id else {
            "planning_count": 0,
            "evaluation_count": 0,
            "guide_count": 0,
            "rubric_count": 0,
            "total_documents": 0,
            "time_saved_hours": 0,
        }
    )

    return render_template(

        "dashboard.html",

        app_name=current_app.config["APP_NAME"],

        version=current_app.config["APP_VERSION"],

        company=current_app.config["COMPANY"],

        stats=stats,

        recent_activity=_recent_activity(user_id)

    )


# ==========================================================
# Actividad reciente (últimos documentos del usuario)
# ==========================================================

_ACTIVITY_META = {

    "planning": {
        "label": "Planificación",
        "icon": "fa-book",
        "color": "blue",
        "endpoint": "planning.index",
    },

    "evaluation": {
        "label": "Evaluación",
        "icon": "fa-file-lines",
        "color": "green",
        "endpoint": "evaluation.index",
    },

    "guide": {
        "label": "Guía",
        "icon": "fa-book-open",
        "color": "purple",
        "endpoint": "guides.index",
    },

    "rubric": {
        "label": "Rúbrica",
        "icon": "fa-table",
        "color": "orange",
        "endpoint": "rubrics.index",
    },

    "pie": {
        "label": "PIE",
        "icon": "fa-user-group",
        "color": "red",
        "endpoint": "pie.index",
    },

}


def _recent_activity(user_id, limit=6):

    if not user_id:

        return []

    items = []

    for doc in persistence_service.list_documents(user_id)[:limit]:

        meta = _ACTIVITY_META.get(
            doc.get("document_type"),
            {
                "label": "Documento",
                "icon": "fa-file",
                "color": "blue",
                "endpoint": "dashboard.home",
            }
        )

        created_display = ""

        if doc.get("created_at"):

            try:

                created_display = datetime.fromisoformat(
                    doc["created_at"]
                ).strftime("%d-%m-%Y %H:%M")

            except (ValueError, TypeError):

                created_display = str(doc["created_at"])

        try:

            module_url = url_for(meta["endpoint"])

        except Exception:

            module_url = url_for("dashboard.home")

        items.append({
            "id": doc.get("id"),
            "title": doc.get("title") or meta["label"],
            "course": doc.get("course"),
            "subject": doc.get("subject"),
            "type_label": meta["label"],
            "icon": meta["icon"],
            "color": meta["color"],
            "module_url": module_url,
            "created_display": created_display,
        })

    return items


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