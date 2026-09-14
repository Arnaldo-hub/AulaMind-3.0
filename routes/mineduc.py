"""
===========================================================
AulaMind Enterprise 3.0
routes/mineduc.py
-----------------------------------------------------------

Planificación MINEDUC (v3.8 Fase 1) — Formato oficial
Planificación Diaria / Clase a Clase.

Rutas:
  GET  /mineduc              → página del generador
  POST /mineduc/api/diaria   → genera plan (JSON estructurado)
  POST /mineduc/pdf          → PDF oficial con tablas reales

Autor:
Biotecno Chile
===========================================================
"""

import logging
import uuid
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
from services.mineduc_service import build_diaria_pdf, generate_diaria

logger = logging.getLogger(__name__)

mineduc = Blueprint("mineduc", __name__, url_prefix="/mineduc")


@mineduc.route("/")
def index():
    if "user_id" not in session:
        return redirect("/auth/login")
    return render_template("mineduc.html")


@mineduc.route("/health")
def health():
    return jsonify(status="ok", service="mineduc", phase="1",
                   format="diaria")


@mineduc.route("/api/diaria", methods=["POST"])
@subscription_required
@limiter.limit("12 per minute")
def api_diaria():
    if "user_id" not in session:
        return jsonify(success=False, error="No autenticado"), 401

    payload = request.get_json(silent=True) or {}

    asignatura = str(payload.get("asignatura", "")).strip()
    curso = str(payload.get("curso", "")).strip()
    unidad = str(payload.get("unidad", "")).strip()
    oat = str(payload.get("oat", "")).strip()
    duracion = str(payload.get("duracion", "")).strip() or "90 minutos"
    fecha = str(payload.get("fecha", "")).strip() \
        or datetime.now().strftime("%d-%m-%Y")
    curso_hora = str(payload.get("curso_hora", "")).strip() \
        or f"{curso} / 1 hora pedagógica"

    # validación básica de largos
    for valor, nombre in ((asignatura, "asignatura"),
                          (curso, "curso"), (unidad, "unidad")):
        if not valor:
            return jsonify(success=False,
                           error=f"El campo '{nombre}' es obligatorio."), 400
        if len(valor) > 300:
            return jsonify(success=False,
                           error=f"'{nombre}' demasiado largo."), 400

    result = generate_diaria({
        "asignatura": asignatura,
        "curso": curso,
        "unidad": unidad,
        "oat": oat,
        "duracion": duracion,
    })

    if not result.get("success"):
        err = result.get("error", "")
        if "no configurada" in err:
            return jsonify(result), 503
        return jsonify(result), 400

    user_id = str(session["user_id"])

    # persistir como documento (JSON) para historial y PDF
    meta = {
        "asignatura": asignatura, "curso": curso, "unidad": unidad,
        "oat": oat, "duracion": duracion, "fecha": fecha,
        "curso_hora": curso_hora,
    }
    document_id = None
    try:
        db = SessionLocal()
        doc = Document(
            user_id=user_id,
            document_type="mineduc_diaria",
            title=f"Planificación Diaria MINEDUC - {asignatura} "
                  f"{curso} - {fecha}",
            content=__import__("json").dumps(
                {"meta": meta, "plan": result["data"]},
                ensure_ascii=False
            ),
        )
        db.add(doc)
        db.commit()
        document_id = doc.id
        db.close()
    except Exception:
        logger.exception("[mineduc] no se pudo guardar documento")

    # consumo + auditoría
    Entitlements.record_generation(user_id)
    try:
        db = SessionLocal()
        db.add(AIGeneration(
            user_id=user_id,
            feature="mineduc_diaria",
            model=Config.OPENAI_MODEL,
            success=True,
            latency_ms=result.get("latency_ms"),
        ))
        db.commit()
        db.close()
    except Exception:
        logger.exception("[mineduc] no se pudo auditar")

    return jsonify(
        success=True,
        meta=meta,
        plan=result["data"],
        document_id=document_id,
    )


@mineduc.route("/pdf", methods=["POST"])
def pdf():
    if "user_id" not in session:
        return jsonify(success=False, error="No autenticado"), 401

    import json as _json
    payload = request.get_json(silent=True) or {}
    document_id = payload.get("document_id")

    meta = payload.get("meta") or {}
    plan = payload.get("plan")

    # modo documento guardado: leer de BD
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
            data = _json.loads(doc.content)
            meta = data.get("meta", {})
            plan = data.get("plan")
        except Exception:
            logger.exception("[mineduc] error leyendo documento")
            return jsonify(success=False,
                           error="No se pudo leer el documento."), 500

    if not isinstance(plan, dict) or not plan.get("filas"):
        return jsonify(success=False,
                       error="Sin contenido para PDF."), 400

    try:
        buf = build_diaria_pdf(meta, plan)
    except Exception:
        logger.exception("[mineduc] error generando PDF")
        return jsonify(success=False,
                       error="No se pudo generar el PDF."), 500

    nombre = (meta.get("asignatura", "planificacion") or "planificacion")
    return Response(
        buf.getvalue(),
        mimetype="application/pdf",
        headers={"Content-Disposition":
                 f'attachment; filename="mineduc_diaria_{nombre[:40]}.pdf"'},
    )
