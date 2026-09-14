"""
===========================================================
AulaMind Enterprise 3.0
routes/mineduc.py
-----------------------------------------------------------

Planificación MINEDUC (v3.9) — 5 formatos oficiales:
unidad, anual (Gantt), mensual, diaria, invertida.

Rutas:
  GET  /mineduc                 → página del generador
  GET  /mineduc/health          → estado del servicio
  POST /mineduc/api/generate    → genera cualquier formato
  POST /mineduc/api/diaria      → alias de generate (tipo=diaria)
  POST /mineduc/pdf             → PDF oficial (por tipo)

Autor:
Biotecno Chile
===========================================================
"""

import json
import logging
from datetime import datetime

from flask import (Blueprint, Response, jsonify, redirect,
                   render_template, request, session)

from config import Config
from database.session import SessionLocal
from extensions import limiter
from models.ai_generation import AIGeneration
from models.document import Document
from security.authorization import subscription_required
from services.entitlements import Entitlements
from services.mineduc_service import NOMBRES_TIPOS, TIPOS, build_pdf, generate

logger = logging.getLogger(__name__)

mineduc = Blueprint("mineduc", __name__, url_prefix="/mineduc")


@mineduc.route("/")
def index():
    if "user_id" not in session:
        return redirect("/auth/login")
    return render_template("mineduc.html")


@mineduc.route("/health")
def health():
    return jsonify(status="ok", service="mineduc", version="3.9",
                   formatos=TIPOS)


def _generar(tipo):
    """Lógica común de generación para los 5 formatos."""
    payload = request.get_json(silent=True) or {}

    asignatura = str(payload.get("asignatura", "")).strip()
    curso = str(payload.get("curso", "")).strip()
    unidad = str(payload.get("unidad", "")).strip()
    oa = str(payload.get("oa", "")).strip()
    oat = str(payload.get("oat", "")).strip()
    duracion = str(payload.get("duracion", "")).strip() or "90 minutos"
    fecha = str(payload.get("fecha", "")).strip() \
        or datetime.now().strftime("%d-%m-%Y")
    curso_hora = str(payload.get("curso_hora", "")).strip() \
        or f"{curso} / 1 hora pedagógica"
    mes = str(payload.get("mes", "")).strip()
    anio = str(payload.get("anio", "")).strip()

    for valor, nombre in ((asignatura, "asignatura"), (curso, "curso")):
        if not valor:
            return jsonify(success=False,
                           error=f"El campo '{nombre}' es "
                                 f"obligatorio."), 400
        if len(valor) > 300:
            return jsonify(success=False,
                           error=f"'{nombre}' demasiado "
                                 f"largo."), 400

    data = {
        "asignatura": asignatura, "curso": curso, "unidad": unidad,
        "oa": oa, "oat": oat, "duracion": duracion, "mes": mes,
        "anio": anio,
    }
    result = generate(tipo, data)

    if not result.get("success"):
        err = result.get("error", "")
        if "no configurada" in err:
            return jsonify(result), 503
        return jsonify(result), 400

    user_id = str(session["user_id"])

    meta = {
        "tipo": tipo,
        "nombre_tipo": NOMBRES_TIPOS[tipo],
        "asignatura": asignatura, "curso": curso, "unidad": unidad,
        "oa": oa, "oat": oat, "duracion": duracion, "fecha": fecha,
        "curso_hora": curso_hora, "mes": mes, "anio": anio,
        "profesor": session.get("user_name", ""),
    }
    document_id = None
    try:
        db = SessionLocal()
        doc = Document(
            user_id=user_id,
            document_type=f"mineduc_{tipo}",
            title=f"{NOMBRES_TIPOS[tipo]} - {asignatura} {curso}"
                  + (f" - {mes}" if tipo == "mensual" and mes else ""),
            content=json.dumps({"meta": meta, "plan": result["data"]},
                               ensure_ascii=False),
        )
        db.add(doc)
        db.commit()
        document_id = doc.id
        db.close()
    except Exception:
        logger.exception("[mineduc] no se pudo guardar documento")

    Entitlements.record_generation(user_id)
    try:
        db = SessionLocal()
        db.add(AIGeneration(
            user_id=user_id,
            feature=f"mineduc_{tipo}",
            model=Config.OPENAI_MODEL,
            success=True,
            latency_ms=result.get("latency_ms"),
        ))
        db.commit()
        db.close()
    except Exception:
        logger.exception("[mineduc] no se pudo auditar")

    return jsonify(success=True, meta=meta, plan=result["data"],
                   document_id=document_id)


@mineduc.route("/api/generate", methods=["POST"])
@subscription_required
@limiter.limit("12 per minute")
def api_generate():
    if "user_id" not in session:
        return jsonify(success=False, error="No autenticado"), 401
    tipo = str((request.get_json(silent=True) or {}).get("tipo", "")).strip()
    return _generar(tipo)


@mineduc.route("/api/diaria", methods=["POST"])
@subscription_required
@limiter.limit("12 per minute")
def api_diaria():
    if "user_id" not in session:
        return jsonify(success=False, error="No autenticado"), 401
    return _generar("diaria")


@mineduc.route("/pdf", methods=["POST"])
def pdf():
    if "user_id" not in session:
        return jsonify(success=False, error="No autenticado"), 401

    payload = request.get_json(silent=True) or {}
    document_id = payload.get("document_id")

    meta = payload.get("meta") or {}
    plan = payload.get("plan")

    if document_id and not plan:
        try:
            db = SessionLocal()
            doc = db.query(Document).filter(
                Document.id == str(document_id),
                Document.user_id == str(session["user_id"]),
            ).first()
            db.close()
            if not doc:
                return jsonify(success=False,
                               error="Documento no encontrado."), 404
            data = json.loads(doc.content)
            meta = data.get("meta", {})
            plan = data.get("plan")
        except Exception:
            logger.exception("[mineduc] error leyendo documento")
            return jsonify(success=False,
                           error="No se pudo leer el documento."), 500

    tipo = meta.get("tipo", "diaria")
    if tipo not in TIPOS:
        return jsonify(success=False, error="Tipo de documento "
                                            "inválido."), 400

    if not isinstance(plan, dict) or not plan.get("filas"):
        return jsonify(success=False, error="Sin contenido para "
                                            "PDF."), 400

    try:
        buf = build_pdf(tipo, meta, plan)
    except Exception:
        logger.exception("[mineduc] error generando PDF")
        return jsonify(success=False,
                       error="No se pudo generar el PDF."), 500

    nombre = (meta.get("asignatura", "planificacion")
              or "planificacion")
    return Response(
        buf.getvalue(),
        mimetype="application/pdf",
        headers={"Content-Disposition":
                 f'attachment; filename="mineduc_{tipo}_'
                 f'{nombre[:35]}.pdf"'},
    )
