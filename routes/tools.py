"""
===========================================================
AulaMind Enterprise 3.0
routes/tools.py
-----------------------------------------------------------

Herramientas IA de Apoyo (v3.5)

- GET  /tools                página del asistente
- POST /tools/api/chat       genera respuesta IA (consume
                             1 generación del plan)
- POST /tools/download       descarga la conversación en PDF

Autor:
Biotecno Chile
===========================================================
"""

import html
import logging
from datetime import datetime
from io import BytesIO

from flask import (
    Blueprint,
    render_template,
    jsonify,
    session,
    redirect,
    url_for,
    current_app,
    request,
    send_file,
)

from extensions import limiter
from security.authorization import subscription_required
from services.entitlements import Entitlements
from services.tools_service import tools_service

logger = logging.getLogger(__name__)

tools = Blueprint(
    "tools",
    __name__,
    url_prefix="/tools"
)


# ==========================================================
# UTILIDADES
# ==========================================================

def is_logged():
    return session.get("user_id") is not None


def login_required(view):
    from functools import wraps

    @wraps(view)
    def wrapper(*args, **kwargs):
        if not is_logged():
            return redirect(url_for("auth.login"))
        return view(*args, **kwargs)
    return wrapper


# ==========================================================
# PAGINA
# ==========================================================

@tools.route("/")
@login_required
def index():
    return render_template(
        "tools.html",
        title="Herramientas IA",
        templates=tools_service.list_templates(),
        app_name=current_app.config.get("APP_NAME", "AulaMind Enterprise"),
        version=current_app.config.get("APP_VERSION", "3.0.0"),
    )


# ==========================================================
# CHAT
# ==========================================================

@tools.route("/api/chat", methods=["POST"])
@login_required
@subscription_required
@limiter.limit("30 per minute")
def api_chat():
    try:
        data = request.get_json(silent=True) or {}

        template_id = data.get("template", "libre")
        message = data.get("message", "")

        if not tools_service.is_valid_template(template_id):
            return jsonify({
                "success": False,
                "error": f"Plantilla '{template_id}' no válida."
            }), 400

        if not str(message).strip():
            return jsonify({
                "success": False,
                "error": "El mensaje no puede estar vacío."
            }), 400

        result = tools_service.generate(template_id, message)

        if not isinstance(result, dict) or not result.get("success"):
            return jsonify({
                "success": False,
                "error": result.get("error", "La IA no pudo responder.")
            }), 502

        # Consumir una generación del plan (igual que planificaciones)
        Entitlements.record_generation(session.get("user_id"))

        return jsonify({
            "success": True,
            "template": template_id,
            "response": result.get("content", ""),
            "generated_at": datetime.now().strftime("%d-%m-%Y %H:%M"),
        })

    except Exception:
        logger.exception("Error inesperado en Tools.api_chat()")
        return jsonify({
            "success": False,
            "error": "Error interno al generar la respuesta."
        }), 500


# ==========================================================
# DESCARGA PDF
# ==========================================================

@tools.route("/download", methods=["POST"])
@login_required
def download_pdf():
    """
    Recibe {title, content} y devuelve un PDF descargable
    generado con reportlab (Unicode completo).
    """
    try:
        data = request.get_json(silent=True) or {}

        title = str(data.get("title", "Respuesta AulaMind")).strip()[:120]
        content = str(data.get("content", "")).strip()

        if not content:
            return jsonify({
                "success": False,
                "error": "No hay contenido para exportar."
            }), 400

        buffer = build_pdf(title, content)

        safe_title = re_safe_filename(title)

        return send_file(
            buffer,
            mimetype="application/pdf",
            as_attachment=True,
            download_name=f"{safe_title}.pdf",
        )

    except Exception:
        logger.exception("Error en Tools.download_pdf()")
        return jsonify({
            "success": False,
            "error": "No se pudo generar el PDF."
        }), 500


def re_safe_filename(name):
    import re
    name = re.sub(r'[^A-Za-z0-9áéíóúñÁÉÍÓÚÑ _-]+', "", name)
    return name.strip().replace(" ", "_")[:60] or "AulaMind"


def build_pdf(title, content):
    """Genera el PDF con reportlab (Helvetica, Unicode latino OK)."""
    from reportlab.lib.pagesizes import letter
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import cm
    from reportlab.platypus import (
        SimpleDocTemplate, Paragraph, Spacer, HRFlowable,
    )

    buffer = BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        leftMargin=2 * cm,
        rightMargin=2 * cm,
        topMargin=2 * cm,
        bottomMargin=2 * cm,
        title=title,
        author="AulaMind Enterprise",
    )

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "AulaTitle",
        parent=styles["Title"],
        fontSize=16,
        spaceAfter=12,
        textColor="#1e3a8a",
    )

    body_style = ParagraphStyle(
        "AulaBody",
        parent=styles["Normal"],
        fontSize=11,
        leading=16,
        spaceAfter=8,
    )

    footer_note = (
        f"Generado por AulaMind Enterprise — "
        f"{datetime.now().strftime('%d-%m-%Y %H:%M')}"
    )

    story = [Paragraph(html.escape(title), title_style)]
    story.append(HRFlowable(width="100%", thickness=1, color="#93c5fd"))
    story.append(Spacer(1, 0.5 * cm))

    for paragraph in content.split("\n"):
        text = paragraph.strip()
        if not text:
            story.append(Spacer(1, 0.25 * cm))
            continue
        # Viñetas y negritas simples de markdown
        safe = html.escape(text)
        safe = safe.replace("**", "")
        if safe.startswith(("- ", "* ", "• ")):
            safe = "• " + safe[2:].strip()
        story.append(Paragraph(safe, body_style))

    story.append(Spacer(1, 0.8 * cm))
    story.append(HRFlowable(width="100%", thickness=0.5, color="#cbd5e1"))
    story.append(Spacer(1, 0.2 * cm))
    story.append(Paragraph(
        f'<font size="8" color="#64748b">{html.escape(footer_note)}</font>',
        body_style,
    ))

    doc.build(story)
    buffer.seek(0)
    return buffer


# ==========================================================
# HEALTH
# ==========================================================

@tools.route("/health")
def health():
    return jsonify({
        "module": "Tools",
        "status": "running",
        "templates": tools_service.list_templates(),
        "server_time": datetime.now().isoformat(),
    })
