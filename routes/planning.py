# ==========================================================
# AulaMind Enterprise 3.0
# routes/planning.py
# MÓDULO 1 - PARTE A
# ==========================================================

from __future__ import annotations

from datetime import datetime

from flask import (
    Blueprint,
    render_template,
    jsonify,
    session,
    redirect,
    url_for,
    current_app,
    request
)

from services.curriculum_service import curriculum_service
from services.planning_service import planning_service
from services.persistence_service import persistence_service


# ==========================================================
# BLUEPRINT
# ==========================================================

planning = Blueprint(
    "planning",
    __name__,
    url_prefix="/planning"
)


# ==========================================================
# UTILIDADES
# ==========================================================

def is_logged():
    """
    Verifica si existe una sesión iniciada.
    """

    return "user_id" in session


def login_required():
    """
    Redirecciona al login si el usuario
    no está autenticado.
    """

    if not is_logged():

        return redirect(
            url_for("auth.login")
        )

    return None


def current_user():

    return {

        "id": session.get("user_id"),

        "name": session.get("user_name"),

        "email": session.get("user_email")

    }


def success(data=None):

    response = {

        "success": True

    }

    if data:

        response.update(data)

    return jsonify(response)


def error(message, status=400):

    return jsonify({

        "success": False,

        "message": message

    }), status


# ==========================================================
# /planning
# ==========================================================

@planning.route("/")
def index():

    auth = login_required()

    if auth:

        return auth

    return render_template(

        "planning.html",

        title="Planning IA",

        user=current_user(),

        app_name=current_app.config.get(
            "APP_NAME",
            "AulaMind Enterprise"
        ),

        version=current_app.config.get(
            "APP_VERSION",
            "3.0.0"
        )

    )


# ==========================================================
# /planning/new
# ==========================================================

@planning.route("/new")
def new_planning():

    auth = login_required()

    if auth:

        return auth

    return render_template(

        "planning.html",

        title="Nueva Planificación",

        user=current_user(),

        app_name=current_app.config.get(
            "APP_NAME",
            "AulaMind Enterprise"
        ),

        version=current_app.config.get(
            "APP_VERSION",
            "3.0.0"
        )

    )


# ==========================================================
# HEALTH
# ==========================================================

@planning.route("/health")
def health():

    return success({

        "module": "Planning",

        "status": "running",

        "version": current_app.config.get(

            "APP_VERSION",

            "3.0.0"

        ),

        "server_time": datetime.now().isoformat()

    })


# ==========================================================
# INFO
# ==========================================================

@planning.route("/info")
def info():

    auth = login_required()

    if auth:

        return auth

    return success({

        "application": current_app.config.get(

            "APP_NAME",

            "AulaMind Enterprise"

        ),

        "version": current_app.config.get(

            "APP_VERSION",

            "3.0.0"

        ),

        "user": current_user(),

        "curriculum": curriculum_service.statistics()

    })


# ==========================================================
# CONTINÚA EN MÓDULO 1 - PARTE B
# ==========================================================
# ==========================================================
# API CURSOS
# ==========================================================

@planning.route("/api/curriculum/courses", methods=["GET"])
def api_courses():

    return jsonify({

        "success": True,

        "courses": curriculum_service.get_courses()

    })


# ==========================================================
# API ASIGNATURAS
# ==========================================================

@planning.route("/api/curriculum/subjects/<course>", methods=["GET"])
def api_subjects(course):

    return jsonify({

        "success": True,

        "subjects": curriculum_service.get_subjects(course)

    })


# ==========================================================
# API UNIDADES
# ==========================================================

@planning.route(
    "/api/curriculum/units/<course>/<subject>",
    methods=["GET"]
)
def api_units(course, subject):

    return jsonify({

        "success": True,

        "units": curriculum_service.get_units(

            course,

            subject

        )

    })


# ==========================================================
# API OA
# ==========================================================

@planning.route(
    "/api/curriculum/objectives/<course>/<subject>/<unit>",
    methods=["GET"]
)
def api_objectives(course, subject, unit):

    return jsonify({

        "success": True,

        "objectives":

            curriculum_service.get_learning_objectives(

                course,

                subject,

                unit

            )

    })
    # ==========================================================
# GENERAR PLANIFICACIÓN IA
# ==========================================================

@planning.route("/generate", methods=["POST"])
def generate():

    auth = login_required()

    if auth:

        return auth

    data = request.get_json()

    if data is None:

        return error(

            "No se recibieron datos.",

            400

        )

    result = planning_service.generate(data)

    if result.get("success"):
        try:
            document_id = persistence_service.save_generated_document(
                user_id=session.get("user_id"),
                school_id=session.get("school_id"),
                document_type="planning",
                payload=data,
                result=result,
            )
            result["document_id"] = document_id
        except Exception as exc:
            current_app.logger.exception("No se pudo persistir la planificación")
            result["persistence_warning"] = str(exc)

    return jsonify(result)
