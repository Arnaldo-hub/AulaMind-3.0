"""
===========================================================
AulaMind Enterprise 3.0
routes/rubrics.py
-----------------------------------------------------------
Módulo de Rúbricas y Listas de Cotejo IA
===========================================================
"""

from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for
from services.rubric_service import RubricService
from security.authorization import subscription_required
from services.persistence_service import persistence_service

rubrics = Blueprint("rubrics", __name__, url_prefix="/rubrics")
rubric_service = RubricService()

@rubrics.route("/")
def index():
    if "user_id" not in session:
        return redirect(url_for("auth.login"))
    stats = persistence_service.dashboard_stats(session["user_id"])
    return render_template("rubrics.html", rubric_count=stats.get("rubric_count", 0), dashboard_stats=stats)

@rubrics.route("/generate", methods=["POST"])
@subscription_required
def generate():
    if "user_id" not in session:
        return jsonify(success=False, error="No autenticado"), 401
    payload = request.get_json() or {}
    try:
        result = rubric_service.generate(payload)
        if result.get("success"):
            document_id = persistence_service.save_generated_document(
                user_id=session["user_id"],
                school_id=session.get("school_id"),
                document_type="rubric",
                payload=payload,
                result=result
            )
            result["document_id"] = document_id
            return jsonify(result)
    except Exception as ex:
        return jsonify(success=False, error=str(ex)), 500

@rubrics.route("/history")
def history():
    if "user_id" not in session:
        return jsonify(success=False, error="No autenticado"), 401
    items = persistence_service.list_documents(session["user_id"], "rubric")
    return jsonify(success=True, items=items)

@rubrics.route("/<document_id>")
def get_document(document_id):
    if "user_id" not in session:
        return jsonify(success=False, error="No autenticado"), 401
    document = persistence_service.get_document(document_id, session["user_id"])
    if document is None:
        return jsonify(success=False, error="Documento no encontrado"), 404
    return jsonify(
        success=True,
        document={
            "id": document.id,
            "title": document.title,
            "document_type": document.document_type,
            "course": document.course,
            "subject": document.subject,
            "unit": document.unit,
            "topic": document.topic,
            "content": document.content,
            "created_at": document.created_at.isoformat() if document.created_at else None
        }
    )

@rubrics.route("/<document_id>", methods=["DELETE"])
def delete_document(document_id):
    if "user_id" not in session:
        return jsonify(success=False, error="No autenticado"), 401
    deleted = persistence_service.delete_document(document_id, session["user_id"])
    if not deleted:
        return jsonify(success=False, error="Documento no encontrado"), 404
    return jsonify(success=True)

@rubrics.route("/export-links/<document_id>")
def export_links(document_id):
    if "user_id" not in session:
        return jsonify(success=False, error="No autenticado"), 401
    document = persistence_service.get_document(document_id, session["user_id"])
    if document is None:
        return jsonify(success=False, error="Documento no encontrado"), 404
    return jsonify(
        success=True,
        word=url_for("export.export_word", document_id=document_id),
        pdf=url_for("export.export_pdf", document_id=document_id)
    )

@rubrics.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        return jsonify(success=False, error="No autenticado"), 401
    stats = persistence_service.dashboard_stats(session["user_id"])
    return jsonify(success=True, stats=stats)

@rubrics.route("/search")
def search():
    if "user_id" not in session:
        return jsonify(success=False, error="No autenticado"), 401
    document_type = request.args.get("type")
    items = persistence_service.list_documents(session["user_id"], document_type)
    return jsonify(success=True, items=items)