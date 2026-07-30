"""
===========================================================
AulaMind Enterprise 3.0
routes/pie.py
-----------------------------------------------------------
Módulo de Adecuaciones Curriculares PIE
===========================================================
"""

from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for
from services.pie_service import PIEService
from services.persistence_service import persistence_service

pie = Blueprint("pie", __name__, url_prefix="/pie")
pie_service = PIEService()

@pie.route("/")
def index():
    if "user_id" not in session:
        return redirect(url_for("auth.login"))
    stats = persistence_service.dashboard_stats(session["user_id"])
    return render_template("pie.html", pie_count=stats.get("pie_count", 0), dashboard_stats=stats)

@pie.route("/generate", methods=["POST"])
def generate():
    if "user_id" not in session:
        return jsonify(success=False, error="No autenticado"), 401
    payload = request.get_json() or {}
    try:
        result = pie_service.generate(payload)
        if result.get("success"):
            document_id = persistence_service.save_generated_document(
                user_id=session["user_id"],
                school_id=session.get("school_id"),
                document_type="pie",
                payload=payload,
                result=result
            )
            result["document_id"] = document_id
            return jsonify(result)
    except Exception as ex:
        return jsonify(success=False, error=str(ex)), 500

@pie.route("/history")
def history():
    if "user_id" not in session:
        return jsonify(success=False, error="No autenticado"), 401
    items = persistence_service.list_documents(session["user_id"], "pie")
    return jsonify(success=True, items=items)

@pie.route("/<document_id>")
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

@pie.route("/<document_id>", methods=["DELETE"])
def delete_document(document_id):
    if "user_id" not in session:
        return jsonify(success=False, error="No autenticado"), 401
    deleted = persistence_service.delete_document(document_id, session["user_id"])
    if not deleted:
        return jsonify(success=False, error="Documento no encontrado"), 404
    return jsonify(success=True)

@pie.route("/export-links/<document_id>")
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

@pie.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        return jsonify(success=False, error="No autenticado"), 401
    stats = persistence_service.dashboard_stats(session["user_id"])
    return jsonify(success=True, stats=stats)

@pie.route("/search")
def search():
    if "user_id" not in session:
        return jsonify(success=False, error="No autenticado"), 401
    document_type = request.args.get("type")
    items = persistence_service.list_documents(session["user_id"], document_type)
    return jsonify(success=True, items=items)