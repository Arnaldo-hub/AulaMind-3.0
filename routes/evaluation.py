"""
===========================================================
AulaMind Enterprise 3.0
routes/evaluation.py
-----------------------------------------------------------

Blueprint del Motor de Evaluaciones IA

Autor:
Biotecno Chile
===========================================================
"""

from flask import (
    Blueprint,
    render_template,
    request,
    jsonify,
    session,
    redirect,
    url_for
)

from services.evaluation_service import EvaluationService
from services.persistence_service import persistence_service

# ==========================================================
# BLUEPRINT
# ==========================================================

evaluation = Blueprint(
    "evaluation",
    __name__,
    url_prefix="/evaluation"
)

# ==========================================================
# SERVICE
# ==========================================================

evaluation_service = EvaluationService()

# ==========================================================
# INDEX
# ==========================================================

@evaluation.route("/", methods=["GET"])
def index():

    if "user_id" not in session:

        return redirect(url_for("auth.login"))

    stats = persistence_service.dashboard_stats(session.get("user_id"))

    return render_template(
        "evaluation.html",
        title="Evaluaciones IA",
        evaluation_count=stats.get("evaluation_count", 0)
    )

# ==========================================================
# GENERAR EVALUACIÓN
# ==========================================================

@evaluation.route("/generate", methods=["POST"])
def generate():

    try:

        data = request.get_json()

        if not data:

            return jsonify({
                "success": False,
                "error": "No se recibieron datos."
            }), 400

        required = [

            "asignatura",
            "curso",
            "unidad",
            "objetivo",
            "tema",
            "tipo",
            "preguntas",
            "dificultad"

        ]

        for campo in required:

            if not data.get(campo):

                return jsonify({

                    "success": False,

                    "error": f"Falta el campo: {campo}"

                }), 400

        if "user_id" not in session:
            return jsonify({"success": False, "error": "No autenticado"}), 401

        resultado = evaluation_service.generate(data)

        if resultado.get("success"):
            try:
                document_id = persistence_service.save_generated_document(
                    user_id=session.get("user_id"),
                    school_id=session.get("school_id"),
                    document_type="evaluation",
                    payload=data,
                    result=resultado,
                )
                resultado["document_id"] = document_id
            except Exception as exc:
                resultado["persistence_warning"] = str(exc)

        return jsonify(resultado)

    except Exception as e:

        return jsonify({

            "success": False,

            "error": str(e)

        }), 500

# ==========================================================
# PREVIEW
# ==========================================================

@evaluation.route("/preview", methods=["POST"])
def preview():

    try:

        contenido = request.json.get("content", "")

        return jsonify({

            "success": True,

            "preview": contenido

        })

    except Exception as e:

        return jsonify({

            "success": False,

            "error": str(e)

        }), 500

# ==========================================================
# SAMPLE
# ==========================================================

@evaluation.route("/sample", methods=["GET"])
def sample():

    ejemplo = """

# Evaluación de Matemática

Curso:
5° Básico

Unidad:
Fracciones

OA:
OA11

------------------------------------------------

I. Selección Múltiple

1.- ¿Cuál es equivalente a 1/2?

A) 2/6

B) 3/6

C) 5/8

D) 4/10

------------------------------------------------

II. Verdadero y Falso

2.- Dos fracciones equivalentes representan la misma cantidad.

------------------------------------------------

III. Desarrollo

3.- Resuelve:

2/5 + 1/5

------------------------------------------------

Puntaje Total:
30 puntos

"""

    return jsonify({

        "success": True,

        "content": ejemplo

    })

# ==========================================================
# EXPORT WORD
# ==========================================================

@evaluation.route("/export/word", methods=["POST"])
def export_word():

    return jsonify({

        "success": False,

        "message": "Disponible en Sprint Export."

    })

# ==========================================================
# EXPORT PDF
# ==========================================================

@evaluation.route("/export/pdf", methods=["POST"])
def export_pdf():

    return jsonify({

        "success": False,

        "message": "Disponible en Sprint Export."

    })

# ==========================================================
# HEALTH
# ==========================================================

@evaluation.route("/health", methods=["GET"])
def health():

    return jsonify({

        "module": "Evaluation Engine",

        "status": "running",

        "version": "1.0"

    })