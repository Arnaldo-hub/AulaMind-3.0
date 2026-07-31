"""
===========================================================
AulaMind Enterprise 3.0
routes/guides.py
===========================================================
"""

from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for
from services.guide_service import GuideService
from security.authorization import subscription_required
from services.persistence_service import persistence_service

guides = Blueprint("guides", __name__, url_prefix="/guides")
guide_service = GuideService()

@guides.route("/")
def index():
    if "user_id" not in session:
        return redirect(url_for("auth.login"))
    stats = persistence_service.dashboard_stats(session["user_id"])
    return render_template("guides.html", guide_count=stats.get("guide_count", 0), dashboard_stats=stats)

@guides.route("/generate", methods=["POST"])
@subscription_required
def generate():
    if "user_id" not in session:
        return jsonify(success=False, error="No autenticado"), 401
    payload = request.get_json() or {}
    try:
        result = guide_service.generate(payload)
        if result.get("success"):
            document_id = persistence_service.save_generated_document(
                user_id=session["user_id"],
                school_id=session.get("school_id"),
                document_type="guide",
                payload=payload,
                result=result
            )
            result["document_id"] = document_id
            return jsonify(result)
    except Exception as ex:
        return jsonify(success=False, error=str(ex)), 500

@guides.route("/history")
def history():
    if "user_id" not in session:
        return jsonify(success=False, error="No autenticado"), 401
    items = persistence_service.list_documents(session["user_id"], "guide")
    return jsonify(success=True, items=items)

@guides.route("/<document_id>")
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

@guides.route("/<document_id>", methods=["DELETE"])
def delete_document(document_id):
    if "user_id" not in session:
        return jsonify(success=False, error="No autenticado"), 401
    deleted = persistence_service.delete_document(document_id, session["user_id"])
    if not deleted:
        return jsonify(success=False, error="Documento no encontrado"), 404
    return jsonify(success=True)

@guides.route("/export-links/<document_id>")
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

@guides.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        return jsonify(success=False, error="No autenticado"), 401
    stats = persistence_service.dashboard_stats(session["user_id"])
    return jsonify(success=True, stats=stats)

@guides.route("/search")
def search():
    if "user_id" not in session:
        return jsonify(success=False, error="No autenticado"), 401
    document_type = request.args.get("type")
    items = persistence_service.list_documents(session["user_id"], document_type)
    return jsonify(success=True, items=items)

@guides.route("/delete/<document_id>", methods=["POST"])
def delete_guide_post(document_id):
    if "user_id" not in session:
        return jsonify(success=False, error="No autenticado"), 401
    deleted = persistence_service.delete_document(document_id, session["user_id"])
    if not deleted:
        return jsonify(success=False, error="Documento no encontrado"), 404
    return jsonify(success=True)