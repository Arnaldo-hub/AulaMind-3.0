# ==========================================================
# AulaMind Enterprise 3.0
# routes/planning.py
# MÓDULO 1 - PARTE A
# ==========================================================

from __future__ import annotations

from datetime import datetime
from functools import wraps

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
from security.authorization import subscription_required
from services.entitlements import Entitlements
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

def is_logged() -> bool:
    """
    Indica si existe una sesión activa.
    """
    return session.get("user_id") is not None


def current_user() -> dict:
    """
    Retorna la información del usuario autenticado.
    """
    return {
        "id": session.get("user_id"),
        "name": session.get("user_name"),
        "email": session.get("user_email")
    }


def login_required(view):
    """
    Decorador para proteger rutas.
    """

    @wraps(view)
    def wrapper(*args, **kwargs):

        if not is_logged():
            return redirect(url_for("auth.login"))

        return view(*args, **kwargs)

    return wrapper


def success(data=None, status=200):

    response = {
        "success": True
    }

    if data:
        response.update(data)

    return jsonify(response), status


def error(message, status=400):

    return jsonify({
        "success": False,
        "message": message
    }), status



# ==========================================================
# /planning
# ==========================================================

@planning.route("/")
@login_required
def index():

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
@login_required
def new_planning():

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
@login_required
def info():

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
# API ASIGNATURAS — CORRECCION DEFINITIVA
# ==========================================================

_SUBJECT_NAME_MAP = {
    "tecnol": "Tecnología",
    "orient": "Orientación", 
    "efi": "Educación Física y Salud",
}

@planning.route("/api/curriculum/subjects/<course>", methods=["GET"])
def api_subjects(course):
    subjects = curriculum_service.get_subjects(course)
    corrected = [_SUBJECT_NAME_MAP.get(s, s) for s in subjects]
    return jsonify({"success": True, "subjects": corrected})

# ==========================================================
# API UNIDADES
# ==========================================================

@planning.route("/api/curriculum/units/<course>/<subject>", methods=["GET"])
def api_units(course, subject):
    return jsonify({
        "success": True,
        "units": curriculum_service.get_units(course, subject)
    })

# ==========================================================
# API OA
# ==========================================================

@planning.route("/api/curriculum/objectives/<course>/<subject>/<unit>", methods=["GET"])
def api_objectives(course, subject, unit):
    return jsonify({
        "success": True,
        "objectives": curriculum_service.get_learning_objectives(course, subject, unit)
    })

# ==========================================================
# GENERAR PLANIFICACIÓN IA
# ==========================================================

@planning.route("/generate", methods=["POST"])
@login_required
@subscription_required
def generate():

    try:

        raw = request.get_json(silent=True)

        if not raw:
            return error(
                "No se recibieron datos.",
                400
            )

        # --------------------------------------------------
        # Normalizar aliases inglés → español.
        #
        # planning.js envía las claves en español
        # (curso, asignatura, unidad, objetivos...), que
        # son las que entiende PlanningService. Se aceptan
        # también las variantes en inglés por compatibilidad.
        # --------------------------------------------------

        aliases = {
            "course": "curso",
            "subject": "asignatura",
            "unit": "unidad",
            "objectives": "objetivos",
            "learning_objectives": "objetivos",
            "selected_objectives": "objetivos",
            "topic": "tema",
            "duration": "duracion",
            "class_type": "tipo",
            "methodology": "metodologia",
            "evaluation": "evaluacion",
            "resources": "recursos",
            "notes": "observaciones",
        }

        data = dict(raw)

        for en, es in aliases.items():

            if en in data:

                if es not in data:
                    data[es] = data[en]

                del data[en]

        required = [
            "curso",
            "asignatura",
            "unidad"
        ]

        missing = [
            field
            for field in required
            if not data.get(field)
        ]

        if missing:

            return error(
                f"Campos obligatorios faltantes: {', '.join(missing)}",
                400
            )

        objectives = data.get("objetivos")

        if objectives is None:
            objectives = []

        if isinstance(objectives, str):
            objectives = [objectives]

        data["objetivos"] = objectives

        current_app.logger.info(
            "Generando planificación %s | %s | %s",
            data["curso"],
            data["asignatura"],
            data["unidad"]
        )

        result = planning_service.generate(data)

        if not isinstance(result, dict):

            return error(
                "planning_service devolvió una respuesta inválida.",
                500
            )

        if result.get("success"):

            # Consumir una generación del trial (si aplica)
            Entitlements.record_generation(
                session.get("user_id")
            )

            try:

                document_id = persistence_service.save_generated_document(

                    user_id=session.get("user_id"),

                    school_id=session.get("school_id"),

                    document_type="planning",

                    payload=data,

                    result=result

                )

                result["document_id"] = document_id

            except Exception:

                current_app.logger.exception(
                    "Error guardando la planificación."
                )

                result["persistence_warning"] = True

        return jsonify(result)

    except Exception:

        current_app.logger.exception(
            "Error inesperado en Planning.generate()"
        )

        return error(
            "Error interno al generar la planificación.",
            500
        )
