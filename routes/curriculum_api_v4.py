"""
===========================================================
AulaMind Enterprise 3.0

Curriculum API v4
===========================================================
"""

from flask import Blueprint, jsonify

from services.curriculum_engine_v4 import curriculum_engine_v4

curriculum_api_v4 = Blueprint(
    "curriculum_api_v4",
    __name__,
    url_prefix="/api/v4/curriculum",
)


# --------------------------------------------------------
# Estadísticas
# --------------------------------------------------------

@curriculum_api_v4.get("/stats")
def stats():

    return jsonify(
        curriculum_engine_v4.statistics()
    )


# --------------------------------------------------------
# Modalidades
# --------------------------------------------------------

@curriculum_api_v4.get("/modalities")
def modalities():

    return jsonify(
        curriculum_engine_v4.modalities()
    )


# --------------------------------------------------------
# Cursos
# --------------------------------------------------------

@curriculum_api_v4.get("/courses/<mode>")
def courses(mode):

    return jsonify(
        curriculum_engine_v4.courses(mode)
    )


# --------------------------------------------------------
# Asignaturas
# --------------------------------------------------------

@curriculum_api_v4.get(
    "/subjects/<mode>/<path:course>"
)
def subjects(mode, course):

    return jsonify(
        curriculum_engine_v4.subjects(
            mode,
            course,
        )
    )


# --------------------------------------------------------
# Registro completo
# --------------------------------------------------------

@curriculum_api_v4.get(
    "/record/<mode>/<path:course>/<path:subject>"
)
def record(
    mode,
    course,
    subject,
):

    record = curriculum_engine_v4.record(
        mode,
        course,
        subject,
    )

    if record is None:

        return jsonify(
            {
                "error": "No encontrado"
            }
        ), 404

    return jsonify(record)