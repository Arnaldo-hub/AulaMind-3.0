"""
===========================================================
AulaMind Enterprise 3.0
services/planning_modalities.py
-----------------------------------------------------------

Modalidades de Planificación (v3.5)

Soporta 5 tipos, todos vinculados a curso/asignatura/OA:

  anual     — Planificación Anual (rango de fechas, carta Gantt)
  mensual   — Planificación Mensual
  diaria    — Planificación Diaria (clase a clase)
  unidad    — Planificación por Unidad (comportamiento actual)
  invertida — Planificación Invertida (clase invertida)

Cada modalidad define su prompt maestro y sus campos
específicos. La validación es centralizada: validate().

Autor: Biotecno Chile
===========================================================
"""

from __future__ import annotations


class PlanningModalities:
    """
    Registro central de modalidades de planificación.
    """

    # ---------------------------------------------------------
    # Catálogo oficial de modalidades
    # ---------------------------------------------------------

    MODALITIES = {
        "anual": {
            "id": "anual",
            "name": "Planificación Anual",
            "description": (
                "Visión completa del año escolar con rango de fechas, "
                "organizada en carta Gantt: unidades en el eje vertical, "
                "semanas/meses en el eje horizontal."
            ),
            "requires_dates": True,
            "prompt": (
                "Genera una PLANIFICACIÓN ANUAL en formato de carta Gantt. "
                "Eje vertical: unidades y OA del año. Eje horizontal: "
                "meses del período {fecha_inicio} a {fecha_termino}. "
                "Para cada unidad indica: semanas de inicio y término, "
                "OA asociados, evaluaciones programadas y hitos "
                "(pruebas, cierres de unidad, actividades institucionales). "
                "Presenta el resultado como tabla markdown con columnas: "
                "Unidad | OA | Inicio | Término | Evaluación."
            ),
            "extra_fields": ["fecha_inicio", "fecha_termino"],
        },
        "mensual": {
            "id": "mensual",
            "name": "Planificación Mensual",
            "description": (
                "Detalle de un mes específico: semanas, actividades, "
                "OA trabajados y evaluaciones del mes."
            ),
            "requires_dates": True,
            "prompt": (
                "Genera una PLANIFICACIÓN MENSUAL para {mes}. "
                "Estructura por semanas (Semana 1 a 4/5): aprendizajes "
                "esperados por semana, actividades principales, OA "
                "trabajados, evaluaciones formativas y recursos. "
                "Cierra con una tabla resumen: Semana | OA | Actividad "
                "central | Evaluación."
            ),
            "extra_fields": ["mes"],
        },
        "diaria": {
            "id": "diaria",
            "name": "Planificación Diaria",
            "description": (
                "Plan de clase diario completo: inicio, desarrollo, "
                "cierre, con tiempos y recursos."
            ),
            "requires_dates": False,
            "prompt": (
                "Genera una PLANIFICACIÓN DIARIA de {duracion}. "
                "Estructura: 1) Inicio (actividad de entrada, "
                "propósito de la clase, 10-15 min). 2) Desarrollo "
                "(actividades secuenciadas con tiempos, estrategias "
                "didácticas, diferenciación DUA). 3) Cierre "
                "(metacognición, evaluación formativa, 10 min). "
                "Incluye: OA, indicadores de evaluación, recursos "
                "y tarea. Asignatura: {asignatura}, Curso: {curso}, "
                "Unidad: {unidad}."
            ),
            "extra_fields": [],
        },
        "unidad": {
            "id": "unidad",
            "name": "Planificación por Unidad",
            "description": (
                "Planificación de una unidad completa: sesiones, "
                "secuencia didáctica y evaluaciones."
            ),
            "requires_dates": False,
            "prompt": (
                "Genera una PLANIFICACIÓN POR UNIDAD. "
                "Incluye: propósito de la unidad, mapa de OA, "
                "secuencia de 6-10 sesiones (cada una con inicio, "
                "desarrollo, cierre), evaluaciones formativas y "
                "sumativa, y criterios de nivel de logro. "
                "Asignatura: {asignatura}, Curso: {curso}, "
                "Unidad: {unidad}, OA: {objetivos}."
            ),
            "extra_fields": [],
        },
        "invertida": {
            "id": "invertida",
            "name": "Planificación Invertida",
            "description": (
                "Clase invertida: contenido previo en casa, "
                "tiempo presencial para práctica y aplicación."
            ),
            "requires_dates": False,
            "prompt": (
                "Genera una PLANIFICACIÓN DE CLASE INVERTIDA. "
                "Estructura en 3 fases: 1) ANTES DE CLASE "
                "(material de estudio autónomo: video/lectura/"
                "guía, con preguntas guía y control de lectura). "
                "2) DURANTE CLASE (aplicación: taller, resolución "
                "de problemas, trabajo colaborativo con tiempos). "
                "3) DESPUÉS DE CLASE (consolidación: tarea, "
                "autoevaluación, actividad de extensión). "
                "Especifica recursos digitales para cada fase y "
                "cómo se verifica que el estudiante realizó la "
                "fase previa. Asignatura: {asignatura}, Curso: "
                "{curso}, Unidad: {unidad}, OA: {objetivos}."
            ),
            "extra_fields": [],
        },
    }

    # ---------------------------------------------------------
    # API pública
    # ---------------------------------------------------------

    @classmethod
    def list(cls):
        """Devuelve el catálogo para poblar el selector de la UI."""
        return [
            {
                "id": m["id"],
                "name": m["name"],
                "description": m["description"],
                "requires_dates": m["requires_dates"],
                "extra_fields": m["extra_fields"],
            }
            for m in cls.MODALITIES.values()
        ]

    @classmethod
    def get(cls, modality_id):
        return cls.MODALITIES.get(modality_id)

    @classmethod
    def is_valid(cls, modality_id):
        return modality_id in cls.MODALITIES

    # ---------------------------------------------------------
    # Construcción del prompt según modalidad
    # ---------------------------------------------------------

    @classmethod
    def build_prompt(cls, modality_id, context):
        """
        context: dict con curso, asignatura, unidad, objetivos,
        duracion, fecha_inicio, fecha_termino, mes.
        """
        modality = cls.get(modality_id)
        if modality is None:
            raise ValueError(f"Modalidad desconocida: {modality_id}")

        prompt = modality["prompt"]

        objetivos = context.get("objetivos", "")
        if isinstance(objetivos, list):
            objetivos = "; ".join(
                o.get("descripcion", str(o)) if isinstance(o, dict) else str(o)
                for o in objetivos
            )

        replacements = {
            "curso": context.get("curso", ""),
            "asignatura": context.get("asignatura", ""),
            "unidad": context.get("unidad", ""),
            "objetivos": objetivos,
            "duracion": context.get("duracion", "90 minutos"),
            "fecha_inicio": context.get("fecha_inicio", "marzo"),
            "fecha_termino": context.get("fecha_termino", "diciembre"),
            "mes": context.get("mes", "el mes indicado"),
        }

        for key, value in replacements.items():
            prompt = prompt.replace("{" + key + "}", str(value))

        return prompt

    # ---------------------------------------------------------
    # Validación centralizada
    # ---------------------------------------------------------

    @classmethod
    def validate(cls, modality_id, data):
        """
        Valida campos obligatorios según modalidad.
        Devuelve (ok, mensaje_error).
        """
        if not cls.is_valid(modality_id):
            return False, f"Modalidad '{modality_id}' no existe."

        base = ["curso", "asignatura"]
        for field in base:
            value = data.get(field, "")
            if not str(value).strip():
                return False, f"El campo '{field}' es obligatorio."

        modality = cls.get(modality_id)

        if modality_id in ("diaria", "unidad", "invertida"):
            if not str(data.get("unidad", "")).strip():
                return False, "El campo 'unidad' es obligatorio."

        if modality_id == "anual":
            for field in ("fecha_inicio", "fecha_termino"):
                if not str(data.get(field, "")).strip():
                    return False, (
                        f"La planificación anual requiere '{field}' "
                        f"(formato AAAA-MM-DD)."
                    )

        if modality_id == "mensual":
            if not str(data.get("mes", "")).strip():
                return False, "La planificación mensual requiere 'mes' (AAAA-MM)."

        return True, ""