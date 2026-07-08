"""
===========================================================
AulaMind Enterprise 3.0
routes/curriculum.py
-----------------------------------------------------------

Administrador del Currículum Nacional

Funciones:

• Dashboard Curricular
• Gestión de Cursos
• Gestión de Asignaturas
• Gestión de Unidades
• Gestión de OA
• Importación del Currículum MINEDUC

Autor:
Biotecno Chile
===========================================================
"""

from pathlib import Path

from flask import (

    Blueprint,

    render_template,

    request,

    jsonify,

    session,

    redirect,

    url_for

)

from werkzeug.utils import secure_filename

from services.curriculum_loader import CurriculumLoader

from database.session import SessionLocal

from models.course import Course
from models.subject import Subject
from models.unit import Unit
from models.learning_objective import LearningObjective


# ==========================================================
# BLUEPRINT
# ==========================================================

curriculum = Blueprint(

    "curriculum",

    __name__,

    url_prefix="/curriculum"

)


# ==========================================================
# CONFIGURACIÓN
# ==========================================================

UPLOAD_FOLDER = "uploads/curriculum"

ALLOWED_EXTENSIONS = {

    "xlsx",

    "csv",

    "json"

}


# ==========================================================
# BASE DE DATOS
# ==========================================================

db = SessionLocal()


# ==========================================================
# SERVICIO
# ==========================================================

loader = CurriculumLoader(db)


# ==========================================================
# UTILIDADES
# ==========================================================

def allowed_file(filename):

    if "." not in filename:

        return False

    extension = filename.rsplit(".", 1)[1].lower()

    return extension in ALLOWED_EXTENSIONS


# ==========================================================
# HOME
# ==========================================================

@curriculum.route("/", methods=["GET"])
def index():

    if "user_id" not in session:

        return redirect(

            url_for("auth.login")

        )

    courses = db.query(Course).count()

    subjects = db.query(Subject).count()

    units = db.query(Unit).count()

    learning_objectives = db.query(

        LearningObjective

    ).count()

    return render_template(

        "curriculum.html",

        title="Motor Curricular",

        total_courses=courses,

        total_subjects=subjects,

        total_units=units,

        total_learning_objectives=learning_objectives

    )


# ==========================================================
# DASHBOARD CURRICULAR
# ==========================================================

@curriculum.route("/dashboard", methods=["GET"])
def dashboard():

    if "user_id" not in session:

        return redirect(

            url_for("auth.login")

        )

    statistics = {

        "courses":

            db.query(Course).count(),

        "subjects":

            db.query(Subject).count(),

        "units":

            db.query(Unit).count(),

        "learning_objectives":

            db.query(

                LearningObjective

            ).count()

    }

    latest_courses = db.query(

        Course

    ).order_by(

        Course.id.desc()

    ).limit(5).all()

    latest_subjects = db.query(

        Subject

    ).order_by(

        Subject.id.desc()

    ).limit(5).all()

    latest_units = db.query(

        Unit

    ).order_by(

        Unit.id.desc()

    ).limit(5).all()

    latest_learning_objectives = db.query(

        LearningObjective

    ).order_by(

        LearningObjective.id.desc()

    ).limit(10).all()

    return render_template(

        "curriculum_dashboard.html",

        title="Dashboard Curricular",

        statistics=statistics,

        latest_courses=latest_courses,

        latest_subjects=latest_subjects,

        latest_units=latest_units,

        latest_learning_objectives=latest_learning_objectives

    )


# ==========================================================
# API ESTADÍSTICAS
# ==========================================================

@curriculum.route("/statistics", methods=["GET"])
def statistics():

    return jsonify({

        "success": True,

        "courses":

            db.query(Course).count(),

        "subjects":

            db.query(Subject).count(),

        "units":

            db.query(Unit).count(),

        "learning_objectives":

            db.query(

                LearningObjective

            ).count()

    })
    