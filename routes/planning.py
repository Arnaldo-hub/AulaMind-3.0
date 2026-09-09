# ==========================================================
# AulaMind Enterprise 3.0
# routes/planning.py
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
from services.planning_service import (
    planning_service,
    PlanningModalities,
)
from services.persistence_service import persistence_service
from routes.curriculum_data import get_subjects_for_course

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
# API MODALIDADES DE PLANIFICACIÓN (v3.5 - Capa 1)
# ==========================================================

@planning.route("/api/planning/modalities", methods=["GET"])
def api_planning_modalities():
    return jsonify({
        "success": True,
        "modalities": PlanningModalities.list()
    })


# ==========================================================
# API CURSOS
# ==========================================================

@planning.route("/api/curriculum/courses", methods=["GET"])
def api_courses():

    courses = curriculum_service.get_courses()

    return jsonify({

        "success": True,

        "courses": courses

    })


# ==========================================================
# RESOLUTOR DE NOMBRES DE ASIGNATURAS (v3.5.4)
# ==========================================================
# El dropdown, las unidades y los OA deben hablar el mismo
# idioma. Traduce variantes (mayúsculas, acentos, la "s"
# final que agrega el frontend: "Matemática"->"Matemáticas",
# y abreviaturas históricas del índice) al nombre EXACTO del
# curriculum_service.
# ==========================================================

import unicodedata


_SUBJECT_ALIASES = {
    "Ciencias Naturales": "Cs. naturales",
    "Educación Física y Salud": "Ed. física",
}


def _norm_subject(s):
    s = unicodedata.normalize("NFKD", s)
    s = "".join(c for c in s if not unicodedata.combining(c))
    return " ".join(s.lower().split())


def _resolve_subject(course, subject):
    """Nombre canónico de la asignatura en el índice del
    servicio. Si no hay match, devuelve el original
    (comportamiento histórico)."""
    if subject in _SUBJECT_ALIASES:
        return _SUBJECT_ALIASES[subject]
    try:
        service_subjects = curriculum_service.get_subjects(course) or []
    except Exception:
        return subject
    if subject in service_subjects:
        return subject
    n = _norm_subject(subject)
    for s in service_subjects:
        if _norm_subject(s) == n:
            return s
    if n.endswith("s"):
        n2 = n[:-1]
        for s in service_subjects:
            if _norm_subject(s) == n2:
                return s
    return subject


# ==========================================================
# API ASIGNATURAS — CORRECCIÓN DEFINITIVA
# ==========================================================

# Mapeo global: abreviaturas → nombres oficiales
_SUBJECT_NAME_MAP = {
    "tecnol": "Tecnología",
    "orient": "Orientación",
    "efi": "Educación Física y Salud",
}


@planning.route("/api/curriculum/subjects/<course>", methods=["GET"])
def api_subjects(course):
    """
    Devuelve asignaturas para un curso.
    Media y Parvularia desde el servicio (alineado con
    unidades y OA); básico desde fuente hardcodeada.
    Solo se muestran asignaturas con unidades cargadas.
    """

    # v3.5.5: Media y Parvularia (NT1/NT2) desde el servicio.
    # v3.5.6: solo asignaturas CON unidades — las vacías
    # (electivos del nuevo currículo marcados
    # PENDIENTE_EXTRACCION_OFICIAL) quedan fuera del
    # dropdown hasta tener su contenido oficial.
    if "Medio" in course or course in ("NT1", "NT2"):
        service_subjects = curriculum_service.get_subjects(course)
        if service_subjects:
            with_units = [
                s for s in service_subjects
                if curriculum_service.get_units(course, s)
            ]
            return jsonify({
                "success": True,
                "subjects": with_units,
                "total": len(with_units)
            })

    subjects = get_subjects_for_course(course)

    if subjects is None:
        return jsonify({
            "success": False,
            "error": f"Curso '{course}' no encontrado"
        }), 404

    corrected = [
        _SUBJECT_NAME_MAP.get(s, s)
        for s in subjects
    ]

    return jsonify({
        "success": True,
        "subjects": corrected,
        "total": len(corrected)
    })


# ==========================================================
# API UNIDADES
# ==========================================================

@planning.route("/api/curriculum/units/<course>/<subject>", methods=["GET"])
def api_units(course, subject):
    # v3.5.4: traducir el nombre del dropdown al nombre
    # canónico del índice (alias/acentos/mayúsculas/s final).
    subject = _resolve_subject(course, subject)
    return jsonify({
        "success": True,
        "units": curriculum_service.get_units(course, subject)
    })


# ==========================================================
# API OA
# ==========================================================

@planning.route("/api/curriculum/objectives/<course>/<subject>/<unit>", methods=["GET"])
def api_objectives(course, subject, unit):
    # v3.5.4: mismo resolvedor que unidades.
    subject = _resolve_subject(course, subject)
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
            # v3.5 Capa 1: modalidades y fechas
            "plan_type": "modalidad_plan",
            "tipo_plan": "modalidad_plan",
            "planning_type": "modalidad_plan",
            "start_date": "fecha_inicio",
            "end_date": "fecha_termino",
            "month": "mes",
        }

        data = dict(raw)

        for en, es in aliases.items():

            if en in data:

                if es not in data:
                    data[es] = data[en]

                del data[en]

        # v3.5 Capa 1: validación según modalidad elegida.
        modality_id = data.get("modalidad_plan") or "unidad"

        if not PlanningModalities.is_valid(modality_id):

            return error(

                f"Modalidad '{modality_id}' no válida. "

                "Usa: anual, mensual, diaria, unidad o invertida.",

                400

            )

        data["modalidad_plan"] = modality_id

        required = PlanningModalities.get(modality_id)[
            "required_fields"
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

            "Generando planificación [%s] %s | %s | %s",

            data["modalidad_plan"],

            data["curso"],

            data["asignatura"],

            data.get("unidad", "")

        )

        result = planning_service.generate(data)

        if not isinstance(result, dict):

            return error(
                "planning_service devolvió una respuesta inválida.",
                500
            )

        if result.get("success"):

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