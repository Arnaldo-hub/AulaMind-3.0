"""
===========================================================
AulaMind Enterprise 3.0
routes/fonoaudiologia.py
-----------------------------------------------------------
Módulo Fonoaudiología Escolar
===========================================================
"""

from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for
from services.fonoaudiologia_service import FonoaudiologiaService
from services.jobs.fonoaudiologia_job import generate_fonoaudiologia_job
from security.authorization import subscription_required
from services.entitlements import Entitlements
from services.persistence_service import persistence_service

fonoaudiologia = Blueprint("fonoaudiologia", __name__, url_prefix="/fonoaudiologia")
fono_service = FonoaudiologiaService()


@fonoaudiologia.route("/")
def index():
    if "user_id" not in session:
        return redirect(url_for("auth.login"))
    stats = persistence_service.dashboard_stats(session["user_id"])
    return render_template("fonoaudiologia.html", dashboard_stats=stats)


@fonoaudiologia.route("/informe", methods=["POST"])
@subscription_required
def generar_informe():
    if "user_id" not in session:
        return jsonify(success=False, error="No autenticado"), 401

    payload = request.get_json() or {}

    # Generación síncrona (compatible con tu infra actual sin RQ)
    result = generate_fonoaudiologia_job(
        user_id=str(session["user_id"]),
        school_id=session.get("school_id"),
        payload=payload,
        tipo="informe",
    )

    return jsonify(result)


@fonoaudiologia.route("/plan", methods=["POST"])
@subscription_required
def generar_plan():
    if "user_id" not in session:
        return jsonify(success=False, error="No autenticado"), 401

    payload = request.get_json() or {}

    result = generate_fonoaudiologia_job(
        user_id=str(session["user_id"]),
        school_id=session.get("school_id"),
        payload=payload,
        tipo="plan",
    )

    return jsonify(result)


@fonoaudiologia.route("/consejos", methods=["POST"])
@subscription_required
def generar_consejos():
    if "user_id" not in session:
        return jsonify(success=False, error="No autenticado"), 401

    payload = request.get_json() or {}

    result = generate_fonoaudiologia_job(
        user_id=str(session["user_id"]),
        school_id=session.get("school_id"),
        payload=payload,
        tipo="consejos",
    )

    return jsonify(result)


@fonoaudiologia.route("/history")
def history():
    if "user_id" not in session:
        return jsonify(success=False, error="No autenticado"), 401

    # Consultar los 3 tipos de documentos fonoaudiológicos
    items = []
    for doc_type in ("fonoaudiologia_informe", "fonoaudiologia_plan", "fonoaudiologia_consejos"):
        items.extend(persistence_service.list_documents(session["user_id"], doc_type))

    # Ordenar por fecha descendente
    items.sort(key=lambda x: x.get("created_at") or "", reverse=True)

    return jsonify(success=True, items=items)


@fonoaudiologia.route("/<document_id>")
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
            "content": document.content,
            "created_at": document.created_at.isoformat() if document.created_at else None,
        }
    )


@fonoaudiologia.route("/<document_id>", methods=["DELETE"])
def delete_document(document_id):
    if "user_id" not in session:
        return jsonify(success=False, error="No autenticado"), 401

    deleted = persistence_service.delete_document(document_id, session["user_id"])
    if not deleted:
        return jsonify(success=False, error="Documento no encontrado"), 404

    return jsonify(success=True)


@fonoaudiologia.route("/export-links/<document_id>")
def export_links(document_id):
    if "user_id" not in session:
        return jsonify(success=False, error="No autenticado"), 401

    document = persistence_service.get_document(document_id, session["user_id"])
    if document is None:
        return jsonify(success=False, error="Documento no encontrado"), 404

    return jsonify(
        success=True,
        word=url_for("export.export_word", document_id=document_id),
        pdf=url_for("export.export_pdf", document_id=document_id),
    )