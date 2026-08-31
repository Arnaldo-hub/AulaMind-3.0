"""
==============================================================
AulaMind Enterprise 3.0
routes/curriculum_api.py
--------------------------------------------------------------

API del Motor Curricular

Permite consultar:

- Cursos
- Asignaturas
- Unidades
- Objetivos de Aprendizaje

Autor:
Biotecno Chile
==============================================================
"""

from flask import (
    Blueprint,
    jsonify,
    request,
    session
)

from services.curriculum_service import CurriculumService


# ==========================================================
# BLUEPRINT
# ==========================================================

curriculum_api = Blueprint(

    "curriculum_api",

    __name__,

    url_prefix="/api/curriculum"

)


# ==========================================================
# SERVICIO
# ==========================================================

curriculum = CurriculumService()


# ==========================================================
# MAPEO DE NOMBRES DE ASIGNATURAS (corrección definitiva)
# ==========================================================
# El singleton carga los JSONs en memoria al iniciar.
# Si los JSONs se corrigen pero el proceso no se reinicia,
# el caché sigue con los nombres viejos.
# SOLUCIÓN: Mapeo directo en los endpoints.
# ==========================================================

_SUBJECT_NAME_MAP = {
    "tecnol": "Tecnología",
    "orient": "Orientación",
    "efi": "Educación Física y Salud",
}


def _normalize_subject_names(subjects):
    """Reemplaza abreviaturas por nombres oficiales."""
    return [
        _SUBJECT_NAME_MAP.get(s, s)
        for s in subjects
    ]


# ==========================================================
# RESPUESTA ERROR
# ==========================================================

def unauthorized():

    return jsonify({

        "success": False,

        "message": "Debe iniciar sesión."

    }), 401


# ==========================================================
# HEALTH
# ==========================================================

@curriculum_api.route(
    "/health",
    methods=["GET"]
)
def health():

    return jsonify({

        "success": True,

        "service": "Curriculum API",

        "version": "1.0.0",

        "status": "running",

        "curriculum": curriculum.health()

    })


# ==========================================================
# ESTADÍSTICAS
# ==========================================================

@curriculum_api.route(
    "/statistics",
    methods=["GET"]
)
def statistics():

    if "user_id" not in session:

        return unauthorized()

    return jsonify({

        "success": True,

        "statistics":

            curriculum.statistics()

    })


# ==========================================================
# CURSOS
# ==========================================================

@curriculum_api.route(
    "/courses",
    methods=["GET"]
)
def courses():

    if "user_id" not in session:

        return unauthorized()

    try:

        data = curriculum.get_courses()

        return jsonify({

            "success": True,

            "total": len(data),

            "courses": data

        })

    except Exception as ex:

        return jsonify({

            "success": False,

            "message": str(ex)

        }), 500
        # ==========================================================
# ASIGNATURAS
# ==========================================================

@curriculum_api.route(
    "/subjects/<path:course>",
    methods=["GET"]
)
def subjects(course):

    if "user_id" not in session:

        return unauthorized()

    try:

        course = course.strip()

        if not curriculum.exists_course(course):

            return jsonify({

                "success": False,

                "message": "Curso no encontrado."

            }), 404

        subjects = curriculum.get_subjects(course)

        # Corrección definitiva: nombres oficiales
        subjects = _normalize_subject_names(subjects)

        return jsonify({

            "success": True,

            "course": course,

            "total": len(subjects),

            "subjects": subjects

        })

    except Exception as ex:

        return jsonify({

            "success": False,

            "message": str(ex)

        }), 500


# ==========================================================
# UNIDADES
# ==========================================================

@curriculum_api.route(
    "/units/<path:course>/<path:subject>",
    methods=["GET"]
)
def units(course, subject):

    if "user_id" not in session:

        return unauthorized()

    try:

        course = course.strip()

        subject = subject.strip()

        if not curriculum.exists_course(course):

            return jsonify({

                "success": False,

                "message": "Curso no encontrado."

            }), 404

        if not curriculum.exists_subject(course, subject):

            return jsonify({

                "success": False,

                "message": "Asignatura no encontrada."

            }), 404

        units = curriculum.get_units(

            course,

            subject

        )

        return jsonify({

            "success": True,

            "course": course,

            "subject": subject,

            "total": len(units),

            "units": units

        })

    except Exception as ex:

        return jsonify({

            "success": False,

            "message": str(ex)

        }), 500


# ==========================================================
# OBJETIVOS DE APRENDIZAJE
# ==========================================================

@curriculum_api.route(
    "/objectives/<path:course>/<path:subject>/<path:unit>",
    methods=["GET"]
)
def objectives(course, subject, unit):

    if "user_id" not in session:

        return unauthorized()

    try:

        course = course.strip()

        subject = subject.strip()

        unit = unit.strip()

        if not curriculum.exists_course(course):

            return jsonify({

                "success": False,

                "message": "Curso no encontrado."

            }), 404

        if not curriculum.exists_subject(course, subject):

            return jsonify({

                "success": False,

                "message": "Asignatura no encontrada."

            }), 404

        if not curriculum.exists_unit(

            course,

            subject,

            unit

        ):

            return jsonify({

                "success": False,

                "message": "Unidad no encontrada."

            }), 404

        objectives = curriculum.get_learning_objectives(

            course,

            subject,

            unit

        )

        data = []

        for oa in objectives:

            data.append({

                "code": oa.get(

                    "codigo",

                    oa.get("code", "")

                ),

                "title": oa.get(

                    "titulo",

                    oa.get("title", "")

                ),

                "description": oa.get(

                    "descripcion",

                    oa.get("description", "")

                )

            })

        return jsonify({

            "success": True,

            "course": course,

            "subject": subject,

            "unit": unit,

            "total": len(data),

            "objectives": data

        })

    except Exception as ex:

        return jsonify({

            "success": False,

            "message": str(ex)

        }), 500
        # ==========================================================
# PLANNING CONTEXT
# ==========================================================

@curriculum_api.route(
    "/planning-context",
    methods=["POST"]
)
def planning_context():

    if "user_id" not in session:

        return unauthorized()

    try:

        data = request.get_json()

        course = data.get("course", "").strip()
        subject = data.get("subject", "").strip()
        unit = data.get("unit", "").strip()

        selected_codes = data.get(
            "learning_objectives",
            []
        )

        context = curriculum.planning_payload(

            course=course,

            subject=subject,

            unit=unit,

            selected_codes=selected_codes

        )

        return jsonify({

            "success": True,

            "data": context

        })

    except Exception as ex:

        return jsonify({

            "success": False,

            "message": str(ex)

        }), 500


# ==========================================================
# EVALUATION CONTEXT
# ==========================================================

@curriculum_api.route(
    "/evaluation-context",
    methods=["POST"]
)
def evaluation_context():

    if "user_id" not in session:

        return unauthorized()

    try:

        data = request.get_json()

        course = data.get("course", "").strip()
        subject = data.get("subject", "").strip()
        unit = data.get("unit", "").strip()

        selected_codes = data.get(
            "learning_objectives",
            []
        )

        context = curriculum.evaluation_payload(

            course=course,

            subject=subject,

            unit=unit,

            selected_codes=selected_codes

        )

        return jsonify({

            "success": True,

            "data": context

        })

    except Exception as ex:

        return jsonify({

            "success": False,

            "message": str(ex)

        }), 500


# ==========================================================
# PROMPT OPENAI
# ==========================================================

@curriculum_api.route(
    "/prompt",
    methods=["POST"]
)
def prompt():

    if "user_id" not in session:

        return unauthorized()

    try:

        data = request.get_json()

        course = data.get("course", "").strip()
        subject = data.get("subject", "").strip()
        unit = data.get("unit", "").strip()

        selected_codes = data.get(
            "learning_objectives",
            []
        )

        prompt = curriculum.build_prompt(

            course=course,

            subject=subject,

            unit=unit,

            selected_codes=selected_codes

        )

        return jsonify({

            "success": True,

            "prompt": prompt

        })

    except Exception as ex:

        return jsonify({

            "success": False,

            "message": str(ex)

        }), 500
        # ==========================================================
# BUSCAR OBJETIVOS DE APRENDIZAJE
# ==========================================================

@curriculum_api.route(
    "/search",
    methods=["GET"]
)
def search_learning_objectives():

    if "user_id" not in session:
        return unauthorized()

    try:

        text = request.args.get("q", "").strip()

        if text == "":

            return jsonify({

                "success": True,

                "total": 0,

                "results": []

            })

        results = curriculum.search_learning_objectives(text)

        return jsonify({

            "success": True,

            "query": text,

            "total": len(results),

            "results": results

        })

    except Exception as ex:

        return jsonify({

            "success": False,

            "message": str(ex)

        }), 500


# ==========================================================
# BUSCAR UNIDADES
# ==========================================================

@curriculum_api.route(
    "/search-units",
    methods=["GET"]
)
def search_units():

    if "user_id" not in session:
        return unauthorized()

    try:

        text = request.args.get("q", "").strip()

        results = curriculum.search_units(text)

        return jsonify({

            "success": True,

            "query": text,

            "total": len(results),

            "results": results

        })

    except Exception as ex:

        return jsonify({

            "success": False,

            "message": str(ex)

        }), 500


# ==========================================================
# EXPORTAR CURRÍCULUM
# ==========================================================

@curriculum_api.route(
    "/export",
    methods=["GET"]
)
def export_curriculum():

    if "user_id" not in session:
        return unauthorized()

    try:

        data = curriculum.export()

        return jsonify({

            "success": True,

            "data": data

        })

    except Exception as ex:

        return jsonify({

            "success": False,

            "message": str(ex)

        }), 500


# ==========================================================
# RECARGAR CURRÍCULUM
# ==========================================================

@curriculum_api.route(
    "/reload",
    methods=["POST"]
)
def reload_curriculum():

    if "user_id" not in session:
        return unauthorized()

    try:

        curriculum.refresh()

        return jsonify({

            "success": True,

            "message": "Currículum recargado correctamente.",

            "statistics": curriculum.statistics()

        })

    except Exception as ex:

        return jsonify({

            "success": False,

            "message": str(ex)

        }), 500


# ==========================================================
# INFORMACIÓN DEL SERVICIO
# ==========================================================

@curriculum_api.route(
    "/info",
    methods=["GET"]
)
def info():

    try:

        return jsonify({

            "success": True,

            "service": curriculum.info()

        })

    except Exception as ex:

        return jsonify({

            "success": False,

            "message": str(ex)

        }), 500


# ==========================================================
# MANEJO GLOBAL DE ERRORES
# ==========================================================

@curriculum_api.errorhandler(404)
def not_found(error):

    return jsonify({

        "success": False,

        "message": "Endpoint no encontrado."

    }), 404


@curriculum_api.errorhandler(405)
def method_not_allowed(error):

    return jsonify({

        "success": False,

        "message": "Método HTTP no permitido."

    }), 405


@curriculum_api.errorhandler(Exception)
def internal_error(error):

    return jsonify({

        "success": False,

        "message": str(error)

    }), 500


# ==========================================================
# FIN DEL ARCHIVO
# ==========================================================