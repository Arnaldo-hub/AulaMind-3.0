# ==========================================================
# AulaMind Enterprise 3.0
# routes/planning.py
# MÓDULO 1 - PARTE A + v3.5 MODALIDADES
# ==========================================================
# Cambios v3.5:
#   + GET  /planning/api/planning/modalities
#     Catálogo de las 5 modalidades de planificación.
#   + POST /planning/generate ahora acepta modalidad_plan
#     (anual | mensual | diaria | unidad | invertida) y
#     valida campos según la modalidad elegida.
#   + GET  /planning/api/curriculum/tp/* (especialidades TP)
#     Solo activos si existe services/curriculum_tp_service.py.
#   · Compatibilidad total: sin modalidad_plan opera como
#     planificación por unidad (comportamiento actual).
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

# ----------------------------------------------------------
# Especialidades TP (opcional): si el módulo aún no existe
# en el repo, estos endpoints responden 404 controlado y
# el resto del blueprint funciona con normalidad.
# ----------------------------------------------------------

try:
    from services.curriculum_tp_service import curriculum_tp_service
    TP_AVAILABLE = True
except ImportError:
    curriculum_tp_service = None
    TP_AVAILABLE = False


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
# API MODALIDADES DE PLANIFICACIÓN (v3.5)
# ==========================================================

@planning.route("/api/planning/modalities", methods=["GET"])
def api_planning_modalities():
    """
    Devuelve el catálogo de modalidades de planificación
    soportadas por el motor IA. El frontend usa este
    endpoint para poblar el selector de tipo de plan.
    """
    return success({

        "modalities": PlanningModalities.list()

    })


# ==========================================================
# CONTINÚA EN MÓDULO 1 - PARTE B
# ==========================================================
# ==========================================================
# API CURSOS
# ==========================================================

@planning.route("/api/curriculum/courses", methods=["GET"])
def api_courses():

    courses = curriculum_service.get_courses()

    # ------------------------------------------------------
    # v3.5: fusionar cursos TP si el módulo está disponible.
    # Los cursos TP se identifican por el sufijo "TP" y se
    # agregan al final del listado, sin duplicar.
    # ------------------------------------------------------

    if TP_AVAILABLE and curriculum_tp_service is not None:

        try:

            existing = {c["name"] for c in courses}

            for c in curriculum_tp_service.get_courses():

                if c["name"] not in existing:

                    courses.append(c)

                    existing.add(c["name"])

        except Exception:

            current_app.logger.exception(
                "No se pudieron fusionar cursos TP."
            )

    return jsonify({

        "success": True,

        "courses": courses

    })


# ==========================================================
# API ASIGNATURAS — CORRECCIÓN DEFINITIVA
# ==========================================================
# El singleton curriculum_service carga los JSONs en memoria
# al iniciar el servidor. Si los JSONs en disco se corrigen
# pero el proceso no se reinicia, el caché en memoria sigue
# con los nombres viejos.
#
# SOLUCIÓN: Mapeo directo en el endpoint. No depende de
# archivos en disco ni de caché. Funciona siempre.
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
    Aplica corrección de nombres abreviados antes de enviar
    al frontend, garantizando que siempre se muestren los
    nombres oficiales completos.
    """
    subjects = curriculum_service.get_subjects(course)

    # v3.5: cursos TP consultan al servicio TP
    if not subjects and TP_AVAILABLE and "TP" in course:

        try:

            return jsonify({

                "success": True,

                "subjects": [
                    s["name"]
                    for s in curriculum_tp_service.get_subjects(
                        course
                    )
                ]

            })

        except Exception:

            current_app.logger.exception(
                "Error consultando asignaturas TP."
            )

    # Corrección definitiva: reemplazar abreviaturas
    corrected = [
        _SUBJECT_NAME_MAP.get(s, s)
        for s in subjects
    ]

    return jsonify({
        "success": True,
        "subjects": corrected
    })

# ==========================================================
# API UNIDADES
# ==========================================================

@planning.route("/api/curriculum/units/<course>/<subject>", methods=["GET"])
def api_units(course, subject):

    units = curriculum_service.get_units(course, subject)

    # v3.5: fallback a TP si el curso es técnico-profesional
    if not units and TP_AVAILABLE and "TP" in course:

        try:

            units = [
                u["name"]
                for u in curriculum_tp_service.get_units(
                    course, subject
                )
            ]

        except Exception:

            current_app.logger.exception(
                "Error consultando unidades TP."
            )

    return jsonify({
        "success": True,
        "units": units
    })

# ==========================================================
# API OA
# ==========================================================

@planning.route("/api/curriculum/objectives/<course>/<subject>/<unit>", methods=["GET"])
def api_objectives(course, subject, unit):

    objectives = (
        curriculum_service.get_learning_objectives(
            course, subject, unit
        )
    )

    # v3.5: fallback a TP
    if not objectives and TP_AVAILABLE and "TP" in course:

        try:

            objectives = (
                curriculum_tp_service.get_objectives(
                    course, subject, unit
                )
            )

        except Exception:

            current_app.logger.exception(
                "Error consultando OA TP."
            )

    return jsonify({
        "success": True,
        "objectives": objectives
    })

# ==========================================================
# API ESPECIALIDADES TP EXPLÍCITAS (v3.5)
# ==========================================================

@planning.route("/api/curriculum/tp/subjects/<course>", methods=["GET"])
def api_tp_subjects(course):
    """
    Asignaturas (especialidades) para un curso TP.
    Disponible solo si curriculum_tp_service existe.
    """
    if not TP_AVAILABLE:

        return error(
            "Módulo de especialidades TP no disponible.",
            404
        )

    try:

        return success({

            "subjects": curriculum_tp_service.get_subjects(
                course
            )

        })

    except Exception:

        current_app.logger.exception(
            "api_tp_subjects falló."
        )

        return error(
            "Error consultando especialidades TP.",
            500
        )


@planning.route("/api/curriculum/tp/units/<course>/<subject>", methods=["GET"])
def api_tp_units(course, subject):
    """
    Unidades (sectores) de una especialidad TP.
    """
    if not TP_AVAILABLE:

        return error(
            "Módulo de especialidades TP no disponible.",
            404
        )

    try:

        return success({

            "units": curriculum_tp_service.get_units(
                course, subject
            )

        })

    except Exception:

        current_app.logger.exception(
            "api_tp_units falló."
        )

        return error(
            "Error consultando unidades TP.",
            500
        )


@planning.route("/api/curriculum/tp/objectives/<course>/<subject>/<unit>", methods=["GET"])
def api_tp_objectives(course, subject, unit):
    """
    OA de perfil de egreso de una especialidad TP.
    """
    if not TP_AVAILABLE:

        return error(
            "Módulo de especialidades TP no disponible.",
            404
        )

    try:

        return success({

            "objectives": (
                curriculum_tp_service.get_objectives(
                    course, subject, unit
                )
            )

        })

    except Exception:

        current_app.logger.exception(
            "api_tp_objectives falló."
        )

        return error(
            "Error consultando OA TP.",
            500
        )


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
            # v3.5: modalidades y fechas
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

        # --------------------------------------------------
        # v3.5: validación según modalidad elegida.
        #
        # Sin modalidad_plan → "unidad" (comportamiento
        # histórico, compatible con frontend actual).
        # --------------------------------------------------

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

            modality_id,

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