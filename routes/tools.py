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
from database.session import SessionLocal
from models.ai_generation import AIGeneration
from services.tools_service import tools_service
from services.tools_service import (
    generate_image,
    IMAGES_ENABLED,
    IMAGES_DAILY_LIMIT,
    OPENAI_IMAGE_MODEL,
)

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
        images_enabled=IMAGES_ENABLED,
        images_limit=IMAGES_DAILY_LIMIT,
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
# FASE 2: GENERACIÓN DE IMÁGENES (v3.6)
# Límite diario por usuario configurable (default 5/día).
# ==========================================================

def images_used_today(user_id):
    """Cuenta imágenes generadas hoy por el usuario (auditoría)."""
    db = SessionLocal()
    try:
        start = datetime.now().replace(
            hour=0, minute=0, second=0, microsecond=0
        )
        return db.query(AIGeneration).filter(
            AIGeneration.user_id == str(user_id),
            AIGeneration.feature == "herramientas_ia_image",
            AIGeneration.created_at >= start,
        ).count()
    finally:
        db.close()


@tools.route("/api/image", methods=["POST"])
@login_required
@subscription_required
@limiter.limit("10 per minute")
def api_image():
    try:
        data = request.get_json(silent=True) or {}
        prompt = str(data.get("prompt", "")).strip()

        if not IMAGES_ENABLED:
            return jsonify({
                "success": False,
                "error": ("La generación de imágenes no está habilitada "
                          "en este momento."),
            }), 403

        user_id = session.get("user_id")
        used = images_used_today(user_id)

        if used >= IMAGES_DAILY_LIMIT:
            return jsonify({
                "success": False,
                "error": (f"Usaste tus {IMAGES_DAILY_LIMIT} imágenes de "
                          f"hoy. Vuelve mañana."),
            }), 429

        result = generate_image(prompt)

        if not result.get("success"):
            err = result.get("error", "")
            if "no configurada" in err or "no está habilitada" in err:
                return jsonify(result), 503
            return jsonify(result), 400

        # Consumo: cada imagen cuenta como 1 generación del plan
        Entitlements.record_generation(user_id)

        try:
            db = SessionLocal()
            db.add(AIGeneration(
                user_id=str(user_id),
                feature="herramientas_ia_image",
                model=OPENAI_IMAGE_MODEL,
                success=True,
            ))
            db.commit()
            db.close()
        except Exception:
            logger.exception("[tools] no se pudo auditar imagen")

        payload = {
            "success": True,
            "used_today": used + 1,
            "limit": IMAGES_DAILY_LIMIT,
        }
        if result.get("b64"):
            payload["image"] = "data:image/png;base64," + result["b64"]
        else:
            payload["image"] = result["url"]

        return jsonify(payload)

    except Exception:
        logger.exception("Error inesperado en Tools.api_image()")
        return jsonify({
            "success": False,
            "error": "Error interno al generar la imagen.",
        }), 500

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
