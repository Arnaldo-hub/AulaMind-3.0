from flask import Blueprint, jsonify, request, g, current_app
from functools import wraps
from urllib.parse import unquote
import os
import json

# Importar la fuente de verdad hardcodeada (NO depende del singleton en memoria)
from routes.curriculum_data import get_subjects_for_course, COURSE_SUBJECTS

# Importar el servicio SOLO para endpoints que realmente lo necesiten
from services.curriculum_service import CurriculumService

curriculum_api = Blueprint('curriculum', __name__)

# =============================================================================
# Helper: autenticación docente
# =============================================================================
def require_teacher(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not g.user or g.user.get('role') not in ['teacher', 'admin']:
            return jsonify({"success": False, "error": "No autenticado"}), 401
        return f(*args, **kwargs)
    return decorated

# =============================================================================
# ENDPOINT CRÍTICO: /subjects/<course>
# =============================================================================
@curriculum_api.route('/subjects/<path:course_name>', methods=['GET'])
@require_teacher
def get_subjects(course_name):
    course = unquote(course_name).strip()
    subjects = get_subjects_for_course(course)

    if subjects is None:
        return jsonify({
            "success": False,
            "error": f"Curso '{course}' no encontrado",
            "available_courses": list(COURSE_SUBJECTS.keys())
        }), 404

    return jsonify({
        "course": course,
        "subjects": subjects,
        "total": len(subjects),
        "success": True
    })

# =============================================================================
# ENDPOINT: /courses
# =============================================================================
@curriculum_api.route('/courses', methods=['GET'])
@require_teacher
def get_courses():
    courses = list(COURSE_SUBJECTS.keys())
    return jsonify({
        "success": True,
        "courses": courses,
        "total": len(courses)
    })

# =============================================================================
# ENDPOINT: /planning/generate
# =============================================================================
@curriculum_api.route('/planning/generate', methods=['POST'])
@require_teacher
def generate_planning():
    data = request.get_json() or {}
    course = data.get('course')
    subject = data.get('subject')
    unit = data.get('unit')
    learning_objective = data.get('learning_objective')
    duration_hours = data.get('duration_hours', 2)
    methodology = data.get('methodology', 'clase tradicional')
    resources = data.get('resources', [])
    context = data.get('context', '')

    if not all([course, subject, unit, learning_objective]):
        return jsonify({
            "success": False,
            "error": "Faltan campos obligatorios: course, subject, unit, learning_objective"
        }), 400

    try:
        service = CurriculumService()
        result = service.generate_planning(
            course=course, subject=subject, unit=unit,
            learning_objective=learning_objective,
            duration_hours=duration_hours, methodology=methodology,
            resources=resources, context=context
        )
        return jsonify({"success": True, "planning": result})
    except Exception as e:
        current_app.logger.error(f"Error generando planificación: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

# =============================================================================
# ENDPOINT: /reload  (POST)
# =============================================================================
@curriculum_api.route('/reload', methods=['POST'])
@require_teacher
def reload_curriculum():
    try:
        service = CurriculumService()
        service.reload()
        return jsonify({"success": True, "message": "Curriculum recargado correctamente"})
    except Exception as e:
        current_app.logger.error(f"Error recargando curriculum: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

# =============================================================================
# ENDPOINT: /units/<course>/<subject>
# =============================================================================
@curriculum_api.route('/units/<path:course_name>/<path:subject_name>', methods=['GET'])
@require_teacher
def get_units(course_name, subject_name):
    course = unquote(course_name).strip()
    subject = unquote(subject_name).strip()

    try:
        service = CurriculumService()
        units = service.get_units(course=course, subject=subject)
        if units is None:
            return jsonify({"success": False, "error": f"No se encontraron unidades para {subject} en {course}"}), 404
        return jsonify({"success": True, "course": course, "subject": subject, "units": units})
    except Exception as e:
        current_app.logger.error(f"Error obteniendo unidades: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

# =============================================================================
# ENDPOINT: /objectives/<course>/<subject>/<unit>
# =============================================================================
@curriculum_api.route('/objectives/<path:course_name>/<path:subject_name>/<path:unit_name>', methods=['GET'])
@require_teacher
def get_objectives(course_name, subject_name, unit_name):
    course = unquote(course_name).strip()
    subject = unquote(subject_name).strip()
    unit = unquote(unit_name).strip()

    try:
        service = CurriculumService()
        objectives = service.get_objectives(course=course, subject=subject, unit=unit)
        if objectives is None:
            return jsonify({"success": False, "error": f"No se encontraron objetivos para la unidad '{unit}'"}), 404
        return jsonify({"success": True, "course": course, "subject": subject, "unit": unit, "objectives": objectives})
    except Exception as e:
        current_app.logger.error(f"Error obteniendo objetivos: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

# =============================================================================
# ENDPOINT: /indicators/<course>/<subject>/<unit>/<objective>
# =============================================================================
@curriculum_api.route('/indicators/<path:course_name>/<path:subject_name>/<path:unit_name>/<path:objective_name>', methods=['GET'])
@require_teacher
def get_indicators(course_name, subject_name, unit_name, objective_name):
    course = unquote(course_name).strip()
    subject = unquote(subject_name).strip()
    unit = unquote(unit_name).strip()
    objective = unquote(objective_name).strip()

    try:
        service = CurriculumService()
        indicators = service.get_indicators(course=course, subject=subject, unit=unit, objective=objective)
        if indicators is None:
            return jsonify({"success": False, "error": f"No se encontraron indicadores para el objetivo '{objective}'"}), 404
        return jsonify({"success": True, "course": course, "subject": subject, "unit": unit, "objective": objective, "indicators": indicators})
    except Exception as e:
        current_app.logger.error(f"Error obteniendo indicadores: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

# =============================================================================
# ENDPOINT: /evaluate/rubric
# =============================================================================
@curriculum_api.route('/evaluate/rubric', methods=['POST'])
@require_teacher
def generate_rubric():
    data = request.get_json() or {}
    planning_id = data.get('planning_id')
    criteria = data.get('criteria', [])
    levels = data.get('levels', ['Inicial', 'En proceso', 'Satisfactorio', 'Destacado'])

    if not planning_id:
        return jsonify({"success": False, "error": "Falta planning_id"}), 400

    try:
        service = CurriculumService()
        rubric = service.generate_rubric(planning_id=planning_id, criteria=criteria, levels=levels)
        return jsonify({"success": True, "rubric": rubric})
    except Exception as e:
        current_app.logger.error(f"Error generando rúbrica: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

# =============================================================================
# ENDPOINT: /evaluate/guide
# =============================================================================
@curriculum_api.route('/evaluate/guide', methods=['POST'])
@require_teacher
def generate_guide():
    data = request.get_json() or {}
    planning_id = data.get('planning_id')
    focus = data.get('focus', 'general')

    if not planning_id:
        return jsonify({"success": False, "error": "Falta planning_id"}), 400

    try:
        service = CurriculumService()
        guide = service.generate_guide(planning_id=planning_id, focus=focus)
        return jsonify({"success": True, "guide": guide})
    except Exception as e:
        current_app.logger.error(f"Error generando guía: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

# =============================================================================
# ENDPOINT: /evaluate/self-assessment
# =============================================================================
@curriculum_api.route('/evaluate/self-assessment', methods=['POST'])
@require_teacher
def generate_self_assessment():
    data = request.get_json() or {}
    planning_id = data.get('planning_id')
    format_type = data.get('format', 'cuestionario')

    if not planning_id:
        return jsonify({"success": False, "error": "Falta planning_id"}), 400

    try:
        service = CurriculumService()
        assessment = service.generate_self_assessment(planning_id=planning_id, format_type=format_type)
        return jsonify({"success": True, "self_assessment": assessment})
    except Exception as e:
        current_app.logger.error(f"Error generando autoevaluación: {e}")
        return jsonify({"success": False, "error": str(e)}), 500