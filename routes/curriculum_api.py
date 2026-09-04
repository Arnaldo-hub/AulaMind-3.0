"""
==============================================================
AulaMind Enterprise 3.0
routes/curriculum_api.py
--------------------------------------------------------------
API del Motor Curricular — v3.2.1 EMERGENCIA
nFiltra asignaturas por curso al vuelo, sin depender del
servicio en memoria (singleton no se reinicia).
==============================================================
"""

from flask import Blueprint, jsonify, request, session
from services.curriculum_service import CurriculumService


curriculum_api = Blueprint("curriculum_api", __name__, url_prefix="/api/curriculum")
curriculum = CurriculumService()


# ==========================================================
# MAPEO OFICIAL DE ASIGNATURAS POR CURSO (v3.2.1)
# Se aplica en CADA request, independiente del singleton.
# ==========================================================

OFFICIAL_SUBJECTS = {
    "1° Básico": [
        "Lenguaje y Comunicación", "Matemáticas",
        "Historia, Geografía y Ciencias Sociales", "Artes Visuales",
        "Música", "Educación Física y Salud", "Orientación",
        "Tecnología", "Religión", "Ciencias Naturales",
    ],
    "2° Básico": [
        "Lenguaje y Comunicación", "Matemáticas",
        "Historia, Geografía y Ciencias Sociales", "Artes Visuales",
        "Música", "Educación Física y Salud", "Orientación",
        "Tecnología", "Religión", "Ciencias Naturales",
    ],
    "3° Básico": [
        "Lenguaje y Comunicación", "Matemáticas",
        "Historia, Geografía y Ciencias Sociales", "Artes Visuales",
        "Música", "Educación Física y Salud", "Orientación",
        "Tecnología", "Religión", "Ciencias Naturales",
    ],
    "4° Básico": [
        "Lenguaje y Comunicación", "Matemáticas",
        "Historia, Geografía y Ciencias Sociales", "Artes Visuales",
        "Música", "Educación Física y Salud", "Orientación",
        "Tecnología", "Religión", "Ciencias Naturales",
    ],
    "5° Básico": [
        "Lenguaje y comunicación", "Matemáticas",
        "Historia, Geografía y Cs.Sociales", "Artes visuales",
        "Música", "Ed. física", "Orientación", "Tecnología",
        "Religión", "Cs. naturales", "Inglés",
        "Taller de innovación", "Taller",
    ],
    "6° Básico": [
        "Lenguaje y comunicación", "Matemáticas",
        "Historia, Geografía y Cs.Sociales", "Artes visuales",
        "Música", "Ed. física", "Orientación", "Tecnología",
        "Religión", "Cs. naturales", "Inglés",
        "Taller de innovación", "Taller",
    ],
    "7° Básico": [
        "Lengua y Literatura", "Matemática",
        "Historia, Geografía y Ciencias Sociales",
        "Artes Visuales y Música", "Educación Física y Salud",
        "Orientación", "Tecnología", "Religión", "Inglés",
        "Ciencias Naturales", "Taller de Innovación", "Talleres",
    ],
    "8° Básico": [
        "Lengua y Literatura", "Matemática",
        "Historia, Geografía y Ciencias Sociales",
        "Artes Visuales y Música", "Educación Física y Salud",
        "Orientación", "Tecnología", "Religión", "Inglés",
        "Ciencias Naturales", "Taller de Innovación", "Talleres",
    ],
    "1° Medio": [
        "Lengua y Literatura", "Matemática",
        "Historia, Geografía y Ciencias Sociales", "Artes Visuales",
        "Música", "Educación Física y Salud", "Orientación",
        "Tecnología", "Religión", "Inglés", "Ciencias Naturales",
    ],
    "2° Medio": [
        "Lengua y Literatura", "Matemática",
        "Historia, Geografía y Ciencias Sociales", "Artes Visuales",
        "Música", "Educación Física y Salud", "Orientación",
        "Tecnología", "Religión", "Inglés", "Ciencias Naturales",
    ],
    "3° Medio": [
        "Lengua y Literatura", "Matemática",
        "Historia, Geografía y Ciencias Sociales", "Artes Visuales",
        "Música", "Educación Física y Salud", "Orientación",
        "Tecnología", "Religión", "Inglés",
        "Física", "Química", "Biología",
    ],
    "4° Medio": [
        "Lengua y Literatura", "Matemática",
        "Historia, Geografía y Ciencias Sociales", "Artes Visuales",
        "Música", "Educación Física y Salud", "Orientación",
        "Tecnología", "Religión", "Inglés",
        "Física", "Química", "Biología",
    ],
}


def unauthorized():
    return jsonify({"success": False, "message": "Debe iniciar sesión."}), 401


@curriculum_api.route("/health", methods=["GET"])
def health():
    return jsonify({
        "success": True,
        "service": "Curriculum API",
        "version": "3.2.1",
        "status": "running",
        "curriculum": curriculum.health()
    })


@curriculum_api.route("/courses", methods=["GET"])
def courses():
    if "user_id" not in session:
        return unauthorized()
    try:
        data = curriculum.get_courses()
        return jsonify({"success": True, "total": len(data), "courses": data})
    except Exception as ex:
        return jsonify({"success": False, "message": str(ex)}), 500


@curriculum_api.route("/subjects/<path:course>", methods=["GET"])
def subjects(course):
    if "user_id" not in session:
        return unauthorized()
    try:
        course = course.strip()
        if not curriculum.exists_course(course):
            return jsonify({"success": False, "message": "Curso no encontrado."}), 404

        # OBTENER asignaturas del servicio (pueden estar mal)
        raw_subjects = curriculum.get_subjects(course)

        # FILTRAR con el mapeo oficial (v3.2.1 emergencia)
        if course in OFFICIAL_SUBJECTS:
            official = OFFICIAL_SUBJECTS[course]
            # Solo devolver las que están en la lista oficial
            filtered = [s for s in raw_subjects if s in official]
            # Si faltan algunas oficiales, agregarlas
            for off in official:
                if off not in filtered:
                    filtered.append(off)
            # Ordenar según la lista oficial
            order = {name: idx for idx, name in enumerate(official)}
            filtered.sort(key=lambda x: order.get(x, 999))
            subjects = filtered
        else:
            subjects = raw_subjects

        return jsonify({
            "success": True,
            "course": course,
            "total": len(subjects),
            "subjects": subjects
        })
    except Exception as ex:
        return jsonify({"success": False, "message": str(ex)}), 500


@curriculum_api.route("/units/<path:course>/<path:subject>", methods=["GET"])
def units(course, subject):
    if "user_id" not in session:
        return unauthorized()
    try:
        course = course.strip()
        subject = subject.strip()
        if not curriculum.exists_course(course):
            return jsonify({"success": False, "message": "Curso no encontrado."}), 404
        if not curriculum.exists_subject(course, subject):
            return jsonify({"success": False, "message": "Asignatura no encontrada."}), 404
        units = curriculum.get_units(course, subject)
        return jsonify({
            "success": True, "course": course, "subject": subject,
            "total": len(units), "units": units
        })
    except Exception as ex:
        return jsonify({"success": False, "message": str(ex)}), 500


@curriculum_api.route("/objectives/<path:course>/<path:subject>/<path:unit>", methods=["GET"])
def objectives(course, subject, unit):
    if "user_id" not in session:
        return unauthorized()
    try:
        course, subject, unit = course.strip(), subject.strip(), unit.strip()
        if not curriculum.exists_course(course):
            return jsonify({"success": False, "message": "Curso no encontrado."}), 404
        if not curriculum.exists_subject(course, subject):
            return jsonify({"success": False, "message": "Asignatura no encontrada."}), 404
        if not curriculum.exists_unit(course, subject, unit):
            return jsonify({"success": False, "message": "Unidad no encontrada."}), 404
        objectives = curriculum.get_learning_objectives(course, subject, unit)
        data = [{"code": oa.get("code", ""), "description": oa.get("description", "")} for oa in objectives]
        return jsonify({
            "success": True, "course": course, "subject": subject, "unit": unit,
            "total": len(data), "objectives": data
        })
    except Exception as ex:
        return jsonify({"success": False, "message": str(ex)}), 500


@curriculum_api.route("/planning-context", methods=["POST"])
def planning_context():
    if "user_id" not in session:
        return unauthorized()
    try:
        data = request.get_json()
        context = curriculum.planning_payload(
            course=data.get("course", "").strip(),
            subject=data.get("subject", "").strip(),
            unit=data.get("unit", "").strip(),
            selected_codes=data.get("learning_objectives", [])
        )
        return jsonify({"success": True, "data": context})
    except Exception as ex:
        return jsonify({"success": False, "message": str(ex)}), 500


@curriculum_api.route("/evaluation-context", methods=["POST"])
def evaluation_context():
    if "user_id" not in session:
        return unauthorized()
    try:
        data = request.get_json()
        context = curriculum.evaluation_payload(
            course=data.get("course", "").strip(),
            subject=data.get("subject", "").strip(),
            unit=data.get("unit", "").strip(),
            selected_codes=data.get("learning_objectives", [])
        )
        return jsonify({"success": True, "data": context})
    except Exception as ex:
        return jsonify({"success": False, "message": str(ex)}), 500


@curriculum_api.route("/prompt", methods=["POST"])
def prompt():
    if "user_id" not in session:
        return unauthorized()
    try:
        data = request.get_json()
        prompt = curriculum.build_prompt(
            course=data.get("course", "").strip(),
            subject=data.get("subject", "").strip(),
            unit=data.get("unit", "").strip(),
            selected_codes=data.get("learning_objectives", [])
        )
        return jsonify({"success": True, "prompt": prompt})
    except Exception as ex:
        return jsonify({"success": False, "message": str(ex)}), 500


@curriculum_api.route("/search", methods=["GET"])
def search_learning_objectives():
    if "user_id" not in session:
        return unauthorized()
    try:
        text = request.args.get("q", "").strip()
        if text == "":
            return jsonify({"success": True, "total": 0, "results": []})
        results = curriculum.search_learning_objectives(text)
        return jsonify({"success": True, "query": text, "total": len(results), "results": results})
    except Exception as ex:
        return jsonify({"success": False, "message": str(ex)}), 500


@curriculum_api.route("/search-units", methods=["GET"])
def search_units():
    if "user_id" not in session:
        return unauthorized()
    try:
        text = request.args.get("q", "").strip()
        results = curriculum.search_units(text)
        return jsonify({"success": True, "query": text, "total": len(results), "results": results})
    except Exception as ex:
        return jsonify({"success": False, "message": str(ex)}), 500


@curriculum_api.route("/export", methods=["GET"])
def export_curriculum():
    if "user_id" not in session:
        return unauthorized()
    try:
        data = curriculum.export()
        return jsonify({"success": True, "data": data})
    except Exception as ex:
        return jsonify({"success": False, "message": str(ex)}), 500


@curriculum_api.route("/reload", methods=["POST"])
def reload_curriculum():
    if "user_id" not in session:
        return unauthorized()
    try:
        curriculum.reload()
        return jsonify({
            "success": True,
            "message": "Currículum recargado correctamente.",
            "statistics": curriculum.health()
        })
    except Exception as ex:
        return jsonify({"success": False, "message": str(ex)}), 500


@curriculum_api.route("/info", methods=["GET"])
def info():
    try:
        return jsonify({"success": True, "service": curriculum.info()})
    except Exception as ex:
        return jsonify({"success": False, "message": str(ex)}), 500


@curriculum_api.errorhandler(404)
def not_found(error):
    return jsonify({"success": False, "message": "Endpoint no encontrado."}), 404


@curriculum_api.errorhandler(405)
def method_not_allowed(error):
    return jsonify({"success": False, "message": "Método HTTP no permitido."}), 405


@curriculum_api.errorhandler(Exception)
def internal_error(error):
    return jsonify({"success": False, "message": str(error)}), 500
