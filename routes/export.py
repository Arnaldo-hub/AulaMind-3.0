"""
===========================================================
AulaMind Enterprise 3.0
routes/export.py
-----------------------------------------------------------
Motor de Exportación
- Word (.docx)
- PDF
-----------------------------------------------------------
Biotecno Chile
===========================================================
"""

from flask import (
    Blueprint,
    jsonify,
    send_file,
    session
)

from services.persistence_service import persistence_service
from services.export_service import export_service

export = Blueprint(
    "export",
    __name__,
    url_prefix="/export"
)


# ==========================================================
# DESCARGAR WORD
# ==========================================================

@export.route("/word/<document_id>", methods=["GET"])  # ← FIX
def export_word(document_id):

    if "user_id" not in session:

        return jsonify({

            "success": False,
            "error": "No autenticado"

        }), 401

    document = persistence_service.get_document(

        document_id=document_id,
        user_id=session["user_id"]

    )

    if not document:

        return jsonify({

            "success": False,
            "error": "Documento no encontrado"

        }), 404

    stream = export_service.export_word(

        title=document.title,

        content=document.content,

        teacher=session.get("user_name"),

        school=session.get("school_name"),

        subject=document.subject,

        course=document.course

    )

    filename = export_service.filename(

        document.document_type,
        document.subject,
        document.course

    ) + ".docx"

    return send_file(

        stream,

        as_attachment=True,

        download_name=filename,

        mimetype="application/vnd.openxmlformats-officedocument.wordprocessingml.document"

    )


# ==========================================================
# DESCARGAR PDF
# ==========================================================

@export.route("/pdf/<document_id>", methods=["GET"])   # ← FIX
def export_pdf(document_id):

    if "user_id" not in session:

        return jsonify({

            "success": False,
            "error": "No autenticado"

        }), 401

    document = persistence_service.get_document(

        document_id=document_id,
        user_id=session["user_id"]

    )

    if not document:

        return jsonify({

            "success": False,
            "error": "Documento no encontrado"

        }), 404

    stream = export_service.export_pdf(

        title=document.title,

        content=document.content,

        teacher=session.get("user_name"),

        school=session.get("school_name"),

        subject=document.subject,

        course=document.course

    )

    filename = export_service.filename(

        document.document_type,
        document.subject,
        document.course

    ) + ".pdf"

    return send_file(

        stream,

        as_attachment=True,

        download_name=filename,

        mimetype="application/pdf"

    )


# ==========================================================
# INFORMACIÓN DEL DOCUMENTO
# ==========================================================

@export.route("/info/<document_id>", methods=["GET"])  # ← FIX
def document_info(document_id):

    if "user_id" not in session:

        return jsonify({

            "success": False,
            "error": "No autenticado"

        }), 401

    document = persistence_service.get_document(

        document_id=document_id,
        user_id=session["user_id"]

    )

    if not document:

        return jsonify({

            "success": False,
            "error": "Documento no encontrado"

        }), 404

    return jsonify({

        "success": True,

        "document": {

            "id": document.id,
            "title": document.title,
            "type": document.document_type,
            "course": document.course,
            "subject": document.subject,
            "unit": document.unit,
            "topic": document.topic,
            "created_at": (
                document.created_at.isoformat()
                if document.created_at else None
            )

        }

    })


# ==========================================================
# HEALTH
# ==========================================================

@export.route("/health", methods=["GET"])
def health():

    return jsonify({

        "module": "Export Service",

        "status": "running",

        "version": "1.0"

    })