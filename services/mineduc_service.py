"""
===========================================================
AulaMind Enterprise 3.0
services/mineduc_service.py
-----------------------------------------------------------

Planificación MINEDUC — Formato oficial (v3.8 Fase 1).

Fase 1: Planificación Diaria / Clase a Clase (formato #4 de
la Guía de Formatos del Ministerio de Educación de Chile).

Flujo:
  1. La IA recibe los datos de la clase y devuelve SOLO JSON
     estructurado (objetivo + 3 momentos con descripcion,
     recursos y evaluacion).
  2. El JSON se guarda como documento (document_type
     "mineduc_diaria") y se muestra en pantalla como tabla.
  3. El PDF se construye con tablas reales de reportlab,
     reproduciendo el formato oficial del MINEDUC.

Proximas fases: Unidad Didáctica (#1), Mensual (#3),
Anual Gantt (#2), Invertida (#5).

Autor:
Biotecno Chile
===========================================================
"""

import io
import json
import logging
import re
import time

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import Paragraph, Spacer, Table, TableStyle

from services.openai_service import OpenAIService

logger = logging.getLogger(__name__)

openai_service = OpenAIService()

# Momentos fijos del formato oficial diario
MOMENTOS_OFICIALES = [
    "Inicio (15 min): Activación de conocimientos.",
    "Desarrollo (60 min): Conceptualización y práctica.",
    "Cierre (15 min): Síntesis y metacognición.",
]

SYSTEM_PROMPT = (
    "Eres un planificador pedagógico experto en el sistema "
    "educativo chileno, especializado en el formato oficial de "
    "Planificación Diaria del Ministerio de Educación. "
    "Recibirás datos de una clase y debes completar el plan. "
    "REGLAS ESTRICTAS: "
    "1) Responde SOLO con un objeto JSON válido, sin texto "
    "adicional, sin markdown, sin bloques de código. "
    "2) Estructura exacta: "
    '{"objetivo": "texto del objetivo de la clase (OAT)", '
    '"filas": [{"momento": "etiqueta", "descripcion": "...", '
    '"recursos": "...", "evaluacion": "..."}]} '
    "3) Genera UNA fila por cada momento que se te indique, "
    "conservando su etiqueta exacta. "
    "4) Las descripciones deben ser prácticas, con pasos "
    "concretos para el aula chilena, en español. "
    "5) Recursos y evaluación: breves y concretos por momento."
)

USER_PROMPT_TEMPLATE = (
    "Datos de la clase:\n"
    "- Asignatura: {asignatura}\n"
    "- Curso: {curso}\n"
    "- Unidad/Tema: {unidad}\n"
    "- Objetivo de la clase (OAT), si el docente lo indicó: "
    "{oat}\n"
    "- Duración de la clase: {duracion}\n\n"
    "Momentos oficiales a completar (conserva estas etiquetas "
    "exactas en el campo 'momento'):\n{momentos}\n\n"
    "Devuelve SOLO el JSON."
)


# ------------------------------------------------------
# GENERACION (IA -> JSON)
# ------------------------------------------------------

def generate_diaria(data):
    """
    Genera la planificación diaria MINEDUC en JSON.

    data: dict con asignatura, curso, unidad, oat (opcional),
          duracion (opcional, default '90 minutos').

    Devuelve {"success": True, "data": {...}} o
             {"success": False, "error": str}
    """
    asignatura = (data.get("asignatura") or "").strip()
    curso = (data.get("curso") or "").strip()
    unidad = (data.get("unidad") or "").strip()
    oat = (data.get("oat") or "").strip() or "No indicado"
    duracion = (data.get("duracion") or "").strip() or "90 minutos"

    if not asignatura or not curso or not unidad:
        return {
            "success": False,
            "error": "Asignatura, curso y unidad/tema son "
                     "obligatorios.",
        }

    if not openai_service.available():
        return {
            "success": False,
            "error": "OPENAI_API_KEY no configurada.",
        }

    user_prompt = USER_PROMPT_TEMPLATE.format(
        asignatura=asignatura,
        curso=curso,
        unidad=unidad,
        oat=oat,
        duracion=duracion,
        momentos="\n".join(
            f"  {i + 1}. {m}" for i, m in enumerate(MOMENTOS_OFICIALES)
        ),
    )

    started = time.time()
    result = openai_service.generate(SYSTEM_PROMPT, user_prompt)
    latency = int((time.time() - started) * 1000)
    result["latency_ms"] = latency

    if not result.get("success"):
        return result

    parsed = _parse_json(result.get("content", ""))
    if parsed is None:
        logger.warning("[mineduc] JSON inválido de la IA")
        return {
            "success": False,
            "error": ("La IA no devolvió un formato válido. "
                      "Inténtalo nuevamente."),
        }

    validated = _validate_structure(parsed)
    if validated is None:
        return {
            "success": False,
            "error": ("La estructura devuelta por la IA es "
                      "inválida. Inténtalo nuevamente."),
        }

    result["data"] = validated
    return result


def _parse_json(text):
    """Extrae y parsea JSON del texto de la IA (tolerante)."""
    if not text:
        return None
    text = text.strip()
    # quita envoltorios tipo ```json ... ```
    text = re.sub(r"^```(?:json)?\s*", "", text)
    text = re.sub(r"\s*```$", "", text)
    try:
        return json.loads(text)
    except ValueError:
        pass
    # último recurso: primer {...} balanceado
    match = re.search(r"\{.*\}", text, re.S)
    if match:
        try:
            return json.loads(match.group(0))
        except ValueError:
            return None
    return None


def _validate_structure(parsed):
    """
    Valida y normaliza la estructura JSON esperada.
    Devuelve el dict normalizado o None si es inválido.
    """
    if not isinstance(parsed, dict):
        return None

    objetivo = str(parsed.get("objetivo", "")).strip()
    filas = parsed.get("filas")

    if not objetivo or not isinstance(filas, list) or not filas:
        return None

    if len(filas) != len(MOMENTOS_OFICIALES):
        return None

    normalizadas = []
    for oficial, fila in zip(MOMENTOS_OFICIALES, filas):
        if not isinstance(fila, dict):
            return None
        normalizadas.append({
            "momento": oficial,
            "descripcion": str(fila.get("descripcion", "")).strip(),
            "recursos": str(fila.get("recursos", "")).strip(),
            "evaluacion": str(fila.get("evaluacion", "")).strip(),
        })
        if not normalizadas[-1]["descripcion"]:
            return None

    return {"objetivo": objetivo, "filas": normalizadas}


# ------------------------------------------------------
# PDF CON TABLAS REALES (formato oficial MINEDUC)
# ------------------------------------------------------

def build_diaria_pdf(meta, plan):
    """
    Construye el PDF oficial de Planificación Diaria.

    meta: dict con fecha, curso_hora, asignatura, curso, unidad
    plan: dict con objetivo y filas (salida validada de
          generate_diaria).

    Devuelve BytesIO listo para send_file.
    """
    buf = io.BytesIO()
    doc_title = (
        f"Planificación Diaria - {meta.get('asignatura', '')} "
        f"{meta.get('curso', '')}"
    )

    styles = {
        "title": ParagraphStyle(
            "T", fontName="Helvetica-Bold", fontSize=13,
            alignment=1, spaceAfter=8,
        ),
        "cell": ParagraphStyle(
            "C", fontName="Helvetica", fontSize=9, leading=12,
        ),
        "cellb": ParagraphStyle(
            "CB", fontName="Helvetica-Bold", fontSize=9, leading=12,
        ),
        "cellh": ParagraphStyle(
            "CH", fontName="Helvetica-Bold", fontSize=9, leading=12,
            alignment=1,
        ),
    }

    elementos = [Paragraph(doc_title, styles["title"])]

    # ---- Encabezado: Fecha / Curso-Hora / OAT ----
    encabezado = [
        [
            Paragraph("Fecha:", styles["cellb"]),
            Paragraph(meta.get("fecha", ""), styles["cell"]),
            Paragraph("Curso/Hora:", styles["cellb"]),
            Paragraph(meta.get("curso_hora", ""), styles["cell"]),
        ],
        [
            Paragraph("Objetivo de la Clase (OAT):", styles["cellb"]),
            Paragraph(plan.get("objetivo", ""), styles["cell"]),
            "",
            "",
        ],
    ]
    tabla_enc = Table(encabezado, colWidths=[3.2 * cm, 6.4 * cm,
                                             3.2 * cm, 6.4 * cm])
    tabla_enc.setStyle(TableStyle([
        ("SPAN", (1, 1), (3, 1)),
        ("GRID", (0, 0), (-1, -1), 0.8, colors.black),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#EDF2F9")),
        ("BACKGROUND", (2, 0), (2, 0), colors.HexColor("#EDF2F9")),
        ("BACKGROUND", (0, 1), (0, 1), colors.HexColor("#EDF2F9")),
        ("LEFTPADDING", (0, 0), (-1, -1), 4),
        ("RIGHTPADDING", (0, 0), (-1, -1), 4),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    elementos.append(tabla_enc)
    elementos.append(Spacer(1, 0.4 * cm))

    # ---- Tabla principal: momentos x (descripcion, recursos, evaluacion)
    header = [
        Paragraph("Momento de la Clase", styles["cellh"]),
        Paragraph("Descripción de Actividades", styles["cellh"]),
        Paragraph("Recursos", styles["cellh"]),
        Paragraph("Evaluación", styles["cellh"]),
    ]
    datos = [header]
    for fila in plan.get("filas", []):
        datos.append([
            Paragraph(fila.get("momento", ""), styles["cell"]),
            Paragraph(fila.get("descripcion", ""), styles["cell"]),
            Paragraph(fila.get("recursos", ""), styles["cell"]),
            Paragraph(fila.get("evaluacion", ""), styles["cell"]),
        ])

    tabla = Table(
        datos,
        colWidths=[4.2 * cm, 6.6 * cm, 4.2 * cm, 4.2 * cm],
        repeatRows=1,
    )
    tabla.setStyle(TableStyle([
        ("GRID", (0, 0), (-1, -1), 0.8, colors.black),
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#D7E3F4")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 4),
        ("RIGHTPADDING", (0, 0), (-1, -1), 4),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]))
    elementos.append(tabla)

    # ---- Pie de página ----
    elementos.append(Spacer(1, 0.5 * cm))
    elementos.append(Paragraph(
        "Generado con AulaMind - Formato Planificación Diaria "
        "MINEDUC",
        ParagraphStyle("pie", fontName="Helvetica-Oblique",
                       fontSize=8, textColor=colors.HexColor("#6B7280")),
    ))

    from reportlab.platypus import SimpleDocTemplate
    SimpleDocTemplate(
        buf, pagesize=A4,
        leftMargin=1.5 * cm, rightMargin=1.5 * cm,
        topMargin=1.5 * cm, bottomMargin=1.5 * cm,
        title=doc_title[:100],
    ).build(elementos)

    buf.seek(0)
    return buf
