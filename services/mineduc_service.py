"""
===========================================================
AulaMind Enterprise 3.0
services/mineduc_service.py
-----------------------------------------------------------

Planificación MINEDUC — 5 formatos oficiales (v3.9).

Formatos (Guía del Ministerio de Educación de Chile):
  1. unidad    — Planificación por Unidad Didáctica
  2. anual     — Planificación Anual (carta Gantt)
  3. mensual   — Planificación Mensual
  4. diaria    — Planificación Diaria / Clase a Clase
  5. invertida — Planificación Invertida (Flipped Classroom)

Flujo por formato: IA devuelve SOLO JSON estructurado -> se
valida -> se persiste -> se muestra en tabla -> PDF con
tablas reales de reportlab reproduce el formato oficial.

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
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import (Paragraph, SimpleDocTemplate, Spacer,
                                Table, TableStyle)

from services.openai_service import OpenAIService

logger = logging.getLogger(__name__)

openai_service = OpenAIService()

# Meses del año escolar chileno (carta Gantt)
MESES_GANTT = ["Mar", "Abr", "May", "Jun", "Jul", "Ago",
               "Sep", "Oct", "Nov", "Dic"]

MOMENTOS_DIARIA = [
    "Inicio (15 min): Activación de conocimientos.",
    "Desarrollo (60 min): Conceptualización y práctica.",
    "Cierre (15 min): Síntesis y metacognición.",
]

FASES_INVERTIDA = [
    "Antes de la Clase (Estudio autónomo, videos, lecturas)",
    "Durante la Clase (Resolución de dudas, debates, talleres)",
    "Después de la Clase (Aplicación, proyectos, profundización)",
]

SEMANAS_MENSUAL = ["Semana 1", "Semana 2", "Semana 3", "Semana 4"]

TIPOS = ["unidad", "anual", "mensual", "diaria", "invertida"]

NOMBRES_TIPOS = {
    "unidad": "Planificación por Unidad Didáctica",
    "anual": "Planificación Anual (Carta Gantt)",
    "mensual": "Planificación Mensual",
    "diaria": "Planificación Diaria / Clase a Clase",
    "invertida": "Planificación Invertida (Flipped Classroom)",
}

SYSTEM_BASE = (
    "Eres un planificador pedagógico experto en el sistema "
    "educativo chileno, especializado en los formatos oficiales "
    "del Ministerio de Educación. "
    "REGLAS ESTRICTAS: "
    "1) Responde SOLO con un objeto JSON válido, sin texto "
    "adicional, sin markdown, sin bloques de código. "
    "2) Contenido en español, práctico y concreto para el aula "
    "chilena. "
    "3) Si se indica un Objetivo de Aprendizaje (OA) del "
    "Currículum Nacional, alinea todo a ese OA. "
)


def _prompt(tipo, data):
    """Construye el system+user prompt por formato."""
    asig = data.get("asignatura", "")
    curso = data.get("curso", "")
    unidad = data.get("unidad", "")
    oa = data.get("oa", "") or "No seleccionado"
    oat = data.get("oat", "") or "No indicado"
    dur = data.get("duracion", "") or "90 minutos"

    base = (
        f"Datos:\n- Asignatura: {asig}\n- Curso: {curso}\n"
        f"- Unidad/Tema: {unidad}\n- OA del Currículum: {oa}\n"
        f"- OAT del docente: {oat}\n"
    )

    if tipo == "diaria":
        return (SYSTEM_BASE +
                "Formato: Planificación Diaria. Devuelve JSON con "
                'exactamente esta estructura: {"objetivo": "...", '
                '"filas": [{"momento": "etiqueta", "descripcion": '
                '"...", "recursos": "...", "evaluacion": "..."}]}. '
                "Una fila por cada momento oficial, conservando su "
                "etiqueta exacta. REGLAS PEDAGOGICAS OBLIGATORIAS: "
                "a) El objetivo sigue la estructura Accion (verbo "
                "medible) + Contenido + Contexto. "
                "b) Inicio: activar conocimientos previos Y "
                "comunicar explicitamente el objetivo y como seran "
                "evaluados. "
                "c) Desarrollo: tres fases en orden - presentacion "
                "o modelado del docente, practica guiada, practica "
                "independiente (sola o en grupos). "
                "d) Cierre: sintesis de conceptos clave mas "
                "evaluacion formativa rapida (ticket de salida o "
                "equivalente).",
                base + "Momentos oficiales:\n" + "\n".join(
                    f"  {i+1}. {m}" for i, m in enumerate(MOMENTOS_DIARIA))
                + "\n\nDevuelve SOLO el JSON.")

    if tipo == "unidad":
        return (SYSTEM_BASE +
                "Formato: Planificación por Unidad Didáctica. "
                "Devuelve JSON: {\"nombre_unidad\": \"...\", "
                "\"duracion\": \"...\", \"filas\": [{\"oa\": \"...\", "
                "\"indicadores\": \"...\", \"estrategias\": \"...\", "
                "\"recursos\": \"...\"}]}. Genera entre 3 y 5 filas, "
                "una por OA a trabajar en la unidad. REGLAS "
                "PEDAGOGICAS OBLIGATORIAS: "
                "a) Duracion tipica de 6 a 8 semanas. "
                "b) En estrategias, integra las habilidades "
                "(saber hacer) y actitudes (saber ser) asociadas "
                "al OA. "
                "c) Logica de diseno: define primero como "
                "evaluaras (formativa y sumativa: instrumento y "
                "momento) y luego las estrategias; refleja ese "
                "orden en los textos.",
                base + f"- Duración de la unidad: {dur}\n\n"
                "Devuelve SOLO el JSON.")

    if tipo == "anual":
        return (SYSTEM_BASE +
                "Formato: Planificación Anual (carta Gantt). "
                "Devuelve JSON: {\"filas\": [{\"unidad\": \"nombre\", "
                "\"meses\": [\"Mar\", \"May\"]}]}. En 'meses' incluye "
                "SOLO los códigos de mes en que se imparte cada "
                "unidad, elegidos de esta lista exacta: "
                + ", ".join(MESES_GANTT) + ". REGLAS PEDAGOGICAS "
                "OBLIGATORIAS: "
                "a) Genera entre 4 y 6 unidades, numero sugerido "
                "por el MINEDUC para el año escolar. "
                "b) Asegura la cobertura curricular: ningun OA "
                "central de la asignatura puede quedar fuera del "
                "mapeo; cada unidad debe nombrar los OA que cubre. "
                "c) Calendariza con el calendario escolar real: "
                "respeta feriados, las vacaciones de invierno en "
                "Jul y las semanas de evaluacion y retroalimentacion "
                "(no inicies una unidad nueva en esas semanas). "
                "d) La progresion entre unidades debe ser logica "
                "(de lo mas basico a lo mas complejo).",
                base + "- Duración: 1 año escolar\n"
                f"- Anio escolar: {data.get('anio') or 'en curso'}\n\n"
                "Devuelve SOLO el JSON.")

    if tipo == "mensual":
        return (SYSTEM_BASE +
                "Formato: Planificación Mensual. Devuelve JSON: "
                "{\"filas\": [{\"semana\": \"etiqueta\", \"oa\": "
                "\"...\", \"contenidos\": \"...\", \"evaluacion\": "
                "\"...\"}]}. Una fila por cada semana oficial, "
                "conservando la etiqueta exacta. REGLAS "
                "PEDAGOGICAS OBLIGATORIAS: "
                "a) En 'oa' escribe el micro-objetivo o meta de "
                "aprendizaje especifica de esa semana (acotado y "
                "medible), no el OA completo. "
                "b) En 'evaluacion' describe la evidencia concreta "
                "que entregaran los estudiantes: producto, ticket "
                "de salida o tarea especifica. "
                "c) La suma de las 4 semanas debe cubrir el tramo "
                "de la unidad correspondiente a este mes, sin "
                "saltos ni repeticiones.",
                base + f"- Mes: {data.get('mes', '')}\n"
                "Semanas oficiales:\n" + "\n".join(
                    f"  {i+1}. {s}" for i, s in enumerate(SEMANAS_MENSUAL))
                + "\n\nDevuelve SOLO el JSON.")

    if tipo == "invertida":
        return (SYSTEM_BASE +
                "Formato: Planificación Invertida (Flipped "
                "Classroom). Devuelve JSON: {\"meta\": \"...\", "
                "\"filas\": [{\"fase\": \"etiqueta\", \"actividades\": "
                "\"...\", \"rol_docente\": \"...\", \"recursos\": "
                "\"...\"}]}. Una fila por fase oficial, conservando "
                "la etiqueta exacta. REGLAS PEDAGOGICAS "
                "OBLIGATORIAS: "
                "a) Antes de la clase: recurso de estudio "
                "autonomo de maximo 5 a 7 minutos (video corto, "
                "infografia o lectura) mas una tarea de "
                "verificacion breve que asegure que revisaron el "
                "material. "
                "b) Durante la clase: primeros 10 minutos para "
                "resolver dudas detectadas en la tarea previa; "
                "resto con actividades de alta demanda cognitiva "
                "(debate, problemas complejos, proyectos, casos); "
                "el docente es facilitador. "
                "c) Despues de la clase: actividad de extension o "
                "metacognicion (foro, bitacora, transferencia a "
                "un contexto nuevo).",
                base + "Fases oficiales:\n" + "\n".join(
                    f"  {i+1}. {f}" for i, f in enumerate(FASES_INVERTIDA))
                + "\n\nDevuelve SOLO el JSON.")

    raise ValueError("tipo desconocido")


# ------------------------------------------------------
# GENERACION (IA -> JSON)
# ------------------------------------------------------

def generate(tipo, data):
    """
    Genera cualquiera de los 5 formatos MINEDUC.
    Devuelve {"success": True, "data": {...}} o
             {"success": False, "error": str}
    """
    if tipo not in TIPOS:
        return {"success": False, "error": "Tipo de planificación "
                                           "inválido."}

    asignatura = (data.get("asignatura") or "").strip()
    curso = (data.get("curso") or "").strip()
    unidad = (data.get("unidad") or "").strip()

    if not asignatura or not curso:
        return {"success": False,
                "error": "Asignatura y curso son obligatorios."}
    if tipo in ("diaria", "invertida", "unidad") and not unidad:
        return {"success": False,
                "error": "La unidad/tema es obligatorio para este "
                         "formato."}

    if not openai_service.available():
        return {"success": False, "error": "OPENAI_API_KEY no "
                                           "configurada."}

    system, user = _prompt(tipo, data)

    started = time.time()
    result = openai_service.generate(system, user)
    result["latency_ms"] = int((time.time() - started) * 1000)

    if not result.get("success"):
        return result

    parsed = _parse_json(result.get("content", ""))
    if parsed is None:
        return {"success": False,
                "error": "La IA no devolvió un formato válido. "
                         "Inténtalo nuevamente."}

    validated = _validate(tipo, parsed)
    if validated is None:
        return {"success": False,
                "error": "La estructura devuelta por la IA es "
                         "inválida. Inténtalo nuevamente."}

    result["data"] = validated
    return result


def _parse_json(text):
    if not text:
        return None
    text = text.strip()
    text = re.sub(r"^```(?:json)?\s*", "", text)
    text = re.sub(r"\s*```$", "", text)
    try:
        return json.loads(text)
    except ValueError:
        pass
    match = re.search(r"\{.*\}", text, re.S)
    if match:
        try:
            return json.loads(match.group(0))
        except ValueError:
            return None
    return None


def _s(x):
    return str(x or "").strip()


def _validate(tipo, p):
    """Valida y normaliza según el formato. None si es inválido."""
    if not isinstance(p, dict):
        return None

    if tipo == "diaria":
        obj, filas = _s(p.get("objetivo")), p.get("filas")
        if not obj or not isinstance(filas, list) \
                or len(filas) != len(MOMENTOS_DIARIA):
            return None
        return {"objetivo": obj, "filas": [
            {"momento": m,
             "descripcion": _s(f.get("descripcion")),
             "recursos": _s(f.get("recursos")),
             "evaluacion": _s(f.get("evaluacion"))}
            for m, f in zip(MOMENTOS_DIARIA, filas)
        ]} if all(_s(f.get("descripcion")) for f in filas) else None

    if tipo == "unidad":
        nom, dur, filas = _s(p.get("nombre_unidad")), \
            _s(p.get("duracion")), p.get("filas")
        if not nom or not isinstance(filas, list) \
                or not (1 <= len(filas) <= 8):
            return None
        out = [{"oa": _s(f.get("oa")), "indicadores": _s(f.get("indicadores")),
                "estrategias": _s(f.get("estrategias")),
                "recursos": _s(f.get("recursos"))} for f in filas]
        return {"nombre_unidad": nom, "duracion": dur or "4 semanas",
                "filas": out} if all(r["oa"] for r in out) else None

    if tipo == "anual":
        filas = p.get("filas")
        if not isinstance(filas, list) or not (1 <= len(filas) <= 12):
            return None
        out = []
        for f in filas:
            meses = [m for m in (f.get("meses") or [])
                     if m in MESES_GANTT]
            if not _s(f.get("unidad")) or not meses:
                return None
            out.append({"unidad": _s(f.get("unidad")), "meses": meses})
        return {"filas": out}

    if tipo == "mensual":
        filas = p.get("filas")
        if not isinstance(filas, list) \
                or len(filas) != len(SEMANAS_MENSUAL):
            return None
        return {"filas": [
            {"semana": s, "oa": _s(f.get("oa")),
             "contenidos": _s(f.get("contenidos")),
             "evaluacion": _s(f.get("evaluacion"))}
            for s, f in zip(SEMANAS_MENSUAL, filas)
        ]} if all(_s(f.get("oa")) for f in filas) else None

    if tipo == "invertida":
        meta, filas = _s(p.get("meta")), p.get("filas")
        if not meta or not isinstance(filas, list) \
                or len(filas) != len(FASES_INVERTIDA):
            return None
        return {"meta": meta, "filas": [
            {"fase": fa, "actividades": _s(f.get("actividades")),
             "rol_docente": _s(f.get("rol_docente")),
             "recursos": _s(f.get("recursos"))}
            for fa, f in zip(FASES_INVERTIDA, filas)
        ]} if all(_s(f.get("actividades")) for f in filas) else None

    return None


# ------------------------------------------------------
# PDF — tablas reales por formato oficial
# ------------------------------------------------------

_STYLES = {
    "title": ParagraphStyle("T", fontName="Helvetica-Bold",
                            fontSize=13, alignment=1, spaceAfter=8),
    "cell": ParagraphStyle("C", fontName="Helvetica", fontSize=9,
                           leading=12),
    "cellb": ParagraphStyle("CB", fontName="Helvetica-Bold",
                            fontSize=9, leading=12),
    "cellh": ParagraphStyle("CH", fontName="Helvetica-Bold",
                            fontSize=9, leading=12, alignment=1),
    "pie": ParagraphStyle("P", fontName="Helvetica-Oblique",
                          fontSize=8, textColor=colors.HexColor("#6B7280")),
}


def _grid(headers, widths, rows):
    data = [[Paragraph(h, _STYLES["cellh"]) for h in headers]] + rows
    t = Table(data, colWidths=widths, repeatRows=1)
    t.setStyle(TableStyle([
        ("GRID", (0, 0), (-1, -1), 0.8, colors.black),
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#D7E3F4")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 4),
        ("RIGHTPADDING", (0, 0), (-1, -1), 4),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]))
    return t


def _doc(buf, title, landscape_mode=False):
    return SimpleDocTemplate(
        buf, pagesize=landscape(A4) if landscape_mode else A4,
        leftMargin=1.5 * cm, rightMargin=1.5 * cm,
        topMargin=1.5 * cm, bottomMargin=1.5 * cm,
        title=title[:100],
    )


def build_pdf(tipo, meta, plan):
    """Construye el PDF oficial del formato indicado. BytesIO."""
    buf = io.BytesIO()
    asig = meta.get("asignatura", "")
    curso = meta.get("curso", "")
    nombre = NOMBRES_TIPOS.get(tipo, "Planificación")
    titulo = f"{nombre} - {asig} {curso}"
    el = [Paragraph(titulo, _STYLES["title"])]
    el.append(Paragraph(
        f"Asignatura/Curso: {asig} &nbsp;&nbsp;|&nbsp;&nbsp; "
        f"Profesor(a): {meta.get('profesor', '')}",
        _STYLES["cell"]))
    el.append(Spacer(1, 0.3 * cm))

    if tipo == "diaria":
        enc = Table([
            [Paragraph("Fecha:", _STYLES["cellb"]),
             Paragraph(meta.get("fecha", ""), _STYLES["cell"]),
             Paragraph("Curso/Hora:", _STYLES["cellb"]),
             Paragraph(meta.get("curso_hora", ""), _STYLES["cell"])],
            [Paragraph("Objetivo de la Clase (OAT):", _STYLES["cellb"]),
             Paragraph(plan.get("objetivo", ""), _STYLES["cell"]), "", ""],
        ], colWidths=[3.2 * cm, 6.4 * cm, 3.2 * cm, 6.4 * cm])
        enc.setStyle(TableStyle([
            ("SPAN", (1, 1), (3, 1)),
            ("GRID", (0, 0), (-1, -1), 0.8, colors.black),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#EDF2F9")),
            ("BACKGROUND", (2, 0), (2, 0), colors.HexColor("#EDF2F9")),
            ("BACKGROUND", (0, 1), (0, 1), colors.HexColor("#EDF2F9")),
        ]))
        el.append(enc)
        el.append(Spacer(1, 0.4 * cm))
        el.append(_grid(
            ["Momento de la Clase", "Descripción de Actividades",
             "Recursos", "Evaluación"],
            [4.2 * cm, 6.6 * cm, 4.2 * cm, 4.2 * cm],
            [[Paragraph(f["momento"], _STYLES["cell"]),
              Paragraph(f["descripcion"], _STYLES["cell"]),
              Paragraph(f["recursos"], _STYLES["cell"]),
              Paragraph(f["evaluacion"], _STYLES["cell"])]
             for f in plan.get("filas", [])]))

    elif tipo == "unidad":
        enc = Table([
            [Paragraph("Nombre de Unidad:", _STYLES["cellb"]),
             Paragraph(plan.get("nombre_unidad", ""), _STYLES["cell"]),
             Paragraph("Duración (Horas/Semanas):", _STYLES["cellb"]),
             Paragraph(plan.get("duracion", ""), _STYLES["cell"])],
        ], colWidths=[4 * cm, 6 * cm, 4.6 * cm, 4.6 * cm])
        enc.setStyle(TableStyle([
            ("GRID", (0, 0), (-1, -1), 0.8, colors.black),
            ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#EDF2F9")),
            ("BACKGROUND", (2, 0), (2, 0), colors.HexColor("#EDF2F9")),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ]))
        el.append(enc)
        el.append(Spacer(1, 0.4 * cm))
        el.append(_grid(
            ["Objetivos de Aprendizaje (OA)",
             "Indicadores de Evaluación",
             "Estrategias Didácticas/Actividades", "Recursos"],
            [4.4 * cm, 4.6 * cm, 5.6 * cm, 4.6 * cm],
            [[Paragraph(f["oa"], _STYLES["cell"]),
              Paragraph(f["indicadores"], _STYLES["cell"]),
              Paragraph(f["estrategias"], _STYLES["cell"]),
              Paragraph(f["recursos"], _STYLES["cell"])]
             for f in plan.get("filas", [])]))

    elif tipo == "anual":
        w_unidad = 6.4 * cm
        w_mes = (24.6 * cm - w_unidad) / len(MESES_GANTT)
        rows = []
        for f in plan.get("filas", []):
            row = [Paragraph(f["unidad"], _STYLES["cell"])]
            for m in MESES_GANTT:
                row.append(Paragraph(
                    "X" if m in f.get("meses", []) else "",
                    _STYLES["cellh"]))
            rows.append(row)
        el.append(_grid(
            ["Unidades/Meses"] + MESES_GANTT,
            [w_unidad] + [w_mes] * len(MESES_GANTT), rows))
        buf2 = buf
        _doc(buf2, titulo, landscape_mode=True).build(el)
        buf2.seek(0)
        return buf2

    elif tipo == "mensual":
        enc = Table([
            [Paragraph("Mes:", _STYLES["cellb"]),
             Paragraph(meta.get("mes", ""), _STYLES["cell"]),
             Paragraph("Año/Curso:", _STYLES["cellb"]),
             Paragraph(curso, _STYLES["cell"])],
        ], colWidths=[2.6 * cm, 6.4 * cm, 3.2 * cm, 6.4 * cm])
        enc.setStyle(TableStyle([
            ("GRID", (0, 0), (-1, -1), 0.8, colors.black),
            ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#EDF2F9")),
            ("BACKGROUND", (2, 0), (2, 0), colors.HexColor("#EDF2F9")),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ]))
        el.append(enc)
        el.append(Spacer(1, 0.4 * cm))
        el.append(_grid(
            ["Semana", "Objetivos de Aprendizaje (OA)",
             "Contenidos/Habilidades", "Evaluaciones/Evidencias"],
            [2.8 * cm, 5.6 * cm, 5.6 * cm, 5.6 * cm],
            [[Paragraph(f["semana"], _STYLES["cellb"]),
              Paragraph(f["oa"], _STYLES["cell"]),
              Paragraph(f["contenidos"], _STYLES["cell"]),
              Paragraph(f["evaluacion"], _STYLES["cell"])]
             for f in plan.get("filas", [])]))

    elif tipo == "invertida":
        enc = Table([
            [Paragraph("Unidad/Tema:", _STYLES["cellb"]),
             Paragraph(meta.get("unidad", ""), _STYLES["cell"]),
             Paragraph("Meta de Aprendizaje:", _STYLES["cellb"]),
             Paragraph(plan.get("meta", ""), _STYLES["cell"])],
        ], colWidths=[3.4 * cm, 6.2 * cm, 4 * cm, 5 * cm])
        enc.setStyle(TableStyle([
            ("GRID", (0, 0), (-1, -1), 0.8, colors.black),
            ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#EDF2F9")),
            ("BACKGROUND", (2, 0), (2, 0), colors.HexColor("#EDF2F9")),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ]))
        el.append(enc)
        el.append(Spacer(1, 0.4 * cm))
        el.append(_grid(
            ["Fase del Aprendizaje",
             "Estrategias/Actividades del Estudiante",
             "Rol del Docente/Apoyo", "Recursos/Evidencia"],
            [4.4 * cm, 5.4 * cm, 4.4 * cm, 4.8 * cm],
            [[Paragraph(f["fase"], _STYLES["cell"]),
              Paragraph(f["actividades"], _STYLES["cell"]),
              Paragraph(f["rol_docente"], _STYLES["cell"]),
              Paragraph(f["recursos"], _STYLES["cell"])]
             for f in plan.get("filas", [])]))

    el.append(Spacer(1, 0.5 * cm))
    el.append(Paragraph(
        "Generado con AulaMind - Formatos Planificación MINEDUC",
        _STYLES["pie"]))
    _doc(buf, titulo).build(el)
    buf.seek(0)
    return buf
