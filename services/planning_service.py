"""
===========================================================
AulaMind Enterprise 3.0
services/planning_service.py
-----------------------------------------------------------

Planning Engine

Responsabilidades

✓ Validar datos
✓ Preparar contexto curricular
✓ Construir prompts
✓ Comunicarse con OpenAI
✓ Retornar planificación

Autor:
Biotecno Chile
===========================================================
"""

from datetime import datetime
import logging

from services.openai_service import OpenAIService

logger = logging.getLogger(__name__)


# =====================================================
# MODALIDADES DE PLANIFICACIÓN (v3.5 - Capa 1)
# =====================================================
# Las 5 modalidades son "recetas de prompt" sobre el mismo
# motor. Si no llega modalidad_plan, todo opera como
# "unidad" (comportamiento histórico, 100% compatible).
# =====================================================

class PlanningModalities:
    """
    Catálogo central de modalidades de planificación.
    """

    MODALITIES = {
        "anual": {
            "id": "anual",
            "name": "Planificación Anual",
            "description": (
                "Visión completa del año escolar con rango "
                "de fechas, en formato carta Gantt: unidades "
                "en el eje vertical, meses en el horizontal."
            ),
            "required_fields": [
                "curso", "asignatura",
                "fecha_inicio", "fecha_termino",
            ],
            "prompt": (
                "Genera una PLANIFICACIÓN ANUAL en formato "
                "de carta Gantt para el período "
                "{fecha_inicio} a {fecha_termino}. Eje "
                "vertical: unidades del año. Eje horizontal: "
                "meses. Para cada unidad indica semanas de "
                "inicio y término, OA asociados, evaluaciones "
                "programadas y hitos. Cierra con tabla "
                "markdown: Unidad | OA | Inicio | Término | "
                "Evaluación. Curso: {curso}. Asignatura: "
                "{asignatura}."
            ),
        },
        "mensual": {
            "id": "mensual",
            "name": "Planificación Mensual",
            "description": (
                "Detalle de un mes: semanas, actividades, "
                "OA trabajados y evaluaciones del mes."
            ),
            "required_fields": ["curso", "asignatura", "mes"],
            "prompt": (
                "Genera una PLANIFICACIÓN MENSUAL para "
                "{mes}. Estructura por semanas (Semana 1 a "
                "4 o 5): aprendizajes esperados, actividades "
                "principales, OA trabajados, evaluaciones "
                "formativas y recursos. Cierra con tabla "
                "resumen: Semana | OA | Actividad central | "
                "Evaluación. Curso: {curso}. Asignatura: "
                "{asignatura}."
            ),
        },
        "diaria": {
            "id": "diaria",
            "name": "Planificación Diaria",
            "description": (
                "Plan de clase diario: inicio, desarrollo, "
                "cierre, con tiempos y recursos."
            ),
            "required_fields": ["curso", "asignatura", "unidad"],
            "prompt": (
                "Genera una PLANIFICACIÓN DIARIA de "
                "{duracion} para el curso {curso}, "
                "asignatura {asignatura}, unidad {unidad}, "
                "OA: {objetivos}. Estructura: 1) Inicio "
                "(actividad de entrada y propósito, 10-15 "
                "min). 2) Desarrollo (actividades "
                "secuenciadas con tiempos, estrategias "
                "didácticas y diferenciación DUA). 3) Cierre "
                "(metacognición y evaluación formativa, "
                "10 min). Incluye indicadores de evaluación, "
                "recursos y tarea."
            ),
        },
        "unidad": {
            "id": "unidad",
            "name": "Planificación por Unidad",
            "description": (
                "Planificación de una unidad completa: "
                "sesiones, secuencia didáctica y evaluaciones."
            ),
            "required_fields": ["curso", "asignatura", "unidad"],
            "prompt": (
                "Genera una PLANIFICACIÓN POR UNIDAD para "
                "el curso {curso}, asignatura {asignatura}, "
                "unidad {unidad}, OA: {objetivos}. Incluye: "
                "propósito de la unidad, mapa de OA, "
                "secuencia de 6 a 10 sesiones (cada una con "
                "inicio, desarrollo y cierre), evaluaciones "
                "formativas y sumativa, y criterios de nivel "
                "de logro."
            ),
        },
        "invertida": {
            "id": "invertida",
            "name": "Planificación Invertida",
            "description": (
                "Clase invertida: contenido previo en casa "
                "y tiempo presencial para práctica."
            ),
            "required_fields": ["curso", "asignatura", "unidad"],
            "prompt": (
                "Genera una PLANIFICACIÓN DE CLASE "
                "INVERTIDA para el curso {curso}, asignatura "
                "{asignatura}, unidad {unidad}, OA: "
                "{objetivos}. Estructura en 3 fases: 1) "
                "ANTES DE CLASE (material de estudio "
                "autónomo: video, lectura o guía, con "
                "preguntas guía). 2) DURANTE CLASE "
                "(aplicación: taller, resolución de "
                "problemas, trabajo colaborativo con "
                "tiempos). 3) DESPUÉS DE CLASE "
                "(consolidación: tarea, autoevaluación, "
                "extensión). Especifica recursos digitales "
                "por fase y cómo se verifica la fase previa."
            ),
        },
    }

    @classmethod
    def list(cls):
        return [
            {
                "id": m["id"],
                "name": m["name"],
                "description": m["description"],
                "required_fields": m["required_fields"],
            }
            for m in cls.MODALITIES.values()
        ]

    @classmethod
    def get(cls, modality_id):
        return cls.MODALITIES.get(modality_id)

    @classmethod
    def is_valid(cls, modality_id):
        return modality_id in cls.MODALITIES


class PlanningService:
    """
    Motor principal de generación de planificaciones IA.
    """

    # =====================================================
    # CONSTRUCTOR
    # =====================================================

    def __init__(self):
        self.ai = OpenAIService()

    # =====================================================
    # VALIDAR DATOS
    # =====================================================

    @staticmethod
    def validate(data):

        # v3.5 Capa 1: validación según modalidad elegida.
        # Sin modalidad_plan -> "unidad" (comportamiento
        # histórico, idéntico al original).
        modality_id = data.get("modalidad_plan") or "unidad"

        if not PlanningModalities.is_valid(modality_id):
            return False, (
                f"Modalidad '{modality_id}' no válida. "
                "Usa: anual, mensual, diaria, unidad o "
                "invertida."
            )

        required = list(
            PlanningModalities.get(modality_id)["required_fields"]
        )

        for field in required:

            value = data.get(field)

            if value is None:
                return False, f"El campo '{field}' es obligatorio."

            if isinstance(value, str):
                if value.strip() == "":
                    return False, f"El campo '{field}' es obligatorio."

            elif isinstance(value, list):
                if len(value) == 0:
                    return False, f"El campo '{field}' es obligatorio."

        return True, ""

    # =====================================================
    # SANITIZAR
    # =====================================================

    @staticmethod
    def sanitize(data):

        if data is None:
            return {}

        result = {}

        aliases = {
            "course": "curso",
            "subject": "asignatura",
            "unit": "unidad",
            "objectives": "objetivos",
            "learning_objectives": "objetivos",
            "selected_objectives": "objetivos",
            "topic": "tema",
            "duration": "duracion",
            "class_type": "tipo",
            "methodology": "metodologia",
            "evaluation": "evaluacion",
            "resources": "recursos",
            "notes": "observaciones",
            # v3.5 Capa 1: modalidades y fechas
            "plan_type": "modalidad_plan",
            "tipo_plan": "modalidad_plan",
            "planning_type": "modalidad_plan",
            "start_date": "fecha_inicio",
            "end_date": "fecha_termino",
            "month": "mes",
        }

        for key, value in data.items():
            key = aliases.get(key, key)

            if value is None:
                result[key] = ""
                continue
  
            if isinstance(value, list):

                clean = []

                for item in value:

                    if isinstance(item, dict):
                        clean.append(item)
                    else:
                        text = str(item).strip()
                        if text:
                            clean.append(text)

                result[key] = clean

            else:
                result[key] = str(value).strip()

        return result

    # =====================================================
    # CONTEXTO
    # =====================================================

    @staticmethod
    def build_context(data):

        return {

            "modalidad_plan": data.get(
                "modalidad_plan",
                "unidad"
            ),

            "fecha_inicio": data.get("fecha_inicio", ""),

            "fecha_termino": data.get("fecha_termino", ""),

            "mes": data.get("mes", ""),

            "curso": data.get("curso", ""),

            "asignatura": data.get("asignatura", ""),

            "unidad": data.get("unidad", ""),

            "objetivos": data.get(
                "objetivos",
                data.get("objetivo", [])
            ),

            "tema": data.get(
                "tema",
                data.get("unidad", "")
            ),

            "duracion": data.get(
                "duracion",
                "90 minutos"
            ),

            "tipo": data.get(
                "tipo",
                "Clase interactiva"
            ),

            "metodologia": data.get(
                "metodologia",
                "Aprendizaje Activo"
            ),

            "evaluacion": data.get(
                "evaluacion",
                "Formativa"
            ),

            "recursos": data.get(
                "recursos",
                ""
            ),

            "observaciones": data.get(
                "observaciones",
                ""
            )

        }

    # =====================================================
    # FORMATEAR OA
    # =====================================================

    @staticmethod
    def format_objectives(objectives):

        if objectives is None:
            return ""

        if isinstance(objectives, str):
            return objectives

        if not isinstance(objectives, list):
            return str(objectives)

        lines = []

        for item in objectives:

            if isinstance(item, dict):

                code = item.get("code", "")
                description = item.get("description", "")
                if code:

                    lines.append(
                        f"{code}: {description}"
                    )

                else:

                    lines.append(description)

            else:

                lines.append(str(item))

        return "\n".join(lines)

    # =====================================================
    # CONSTRUIR PROMPT
    # =====================================================

    @staticmethod
    def build_prompt(context, objectives):

        # v3.5 Capa 1: si hay modalidad válida distinta del
        # flujo histórico, se usa su prompt maestro con los
        # datos del contexto. "unidad" u otra no listada
        # mantiene el prompt original de siempre.
        modality_id = context.get("modalidad_plan", "unidad")

        if (
            PlanningModalities.is_valid(modality_id)
            and modality_id != "unidad"
        ):

            prompt = PlanningModalities.get(modality_id)["prompt"]

            replacements = {
                "curso": context.get("curso", ""),
                "asignatura": context.get("asignatura", ""),
                "unidad": context.get("unidad", ""),
                "objetivos": objectives,
                "duracion": context.get("duracion", ""),
                "fecha_inicio": context.get("fecha_inicio", ""),
                "fecha_termino": context.get("fecha_termino", ""),
                "mes": context.get("mes", ""),
            }

            for key, value in replacements.items():
                prompt = prompt.replace(
                    "{" + key + "}",
                    str(value)
                )

            return prompt

        return f"""
Eres AulaMind Enterprise 3.0.

Eres un experto en planificación curricular del
Ministerio de Educación de Chile.

Debes generar una planificación pedagógica completa,
profesional y lista para ser utilizada por un docente.

==================================================
DATOS CURRICULARES
==================================================

Curso:
{context["curso"]}

Asignatura:
{context["asignatura"]}

Unidad:
{context["unidad"]}

Tema:
{context["tema"]}

Duración:
{context["duracion"]}

Tipo de clase:
{context["tipo"]}

Metodología:
{context["metodologia"]}

Evaluación:
{context["evaluacion"]}

Recursos:
{context["recursos"]}

Observaciones:
{context["observaciones"]}

==================================================
OBJETIVOS DE APRENDIZAJE
==================================================

{objectives}

==================================================
REQUISITOS
==================================================

La planificación debe incluir obligatoriamente:

• Objetivo general.

• Objetivos específicos.

• Inicio.

• Desarrollo.

• Cierre.

• Recursos.

• Estrategias metodológicas.

• Evaluación diagnóstica.

• Evaluación formativa.

• Evaluación sumativa.

• Instrumento de evaluación.

• Indicadores de logro.

• Tiempo por actividad.

• Preguntas de metacognición.

• Adaptaciones DUA.

• Adaptaciones PIE.

Escribe todo en español.
"""

    # =====================================================
    # ENRIQUECER PROMPT
    # =====================================================

    @staticmethod
    def enrich_prompt(prompt):

        extra = """

==================================================
ESTÁNDARES AULAMIND
==================================================

La planificación debe cumplir con el currículo
vigente del MINEDUC Chile.

Debe incorporar:

• Aprendizaje Activo.

• Aprendizaje Basado en Problemas.

• Trabajo Colaborativo.

• Pensamiento Crítico.

• Comunicación.

• Creatividad.

• Inclusión.

• Diseño Universal para el Aprendizaje.

• Estrategias PIE.

• TIC.

• Evaluación Formativa.

==================================================
FORMATO
==================================================

Utiliza títulos.

Utiliza subtítulos.

Utiliza listas.

La respuesta debe quedar lista para copiar
directamente a Word.

No inventes Objetivos de Aprendizaje.

Respeta exactamente los OA entregados.
"""

        return prompt + extra

    # =====================================================
    # VALIDAR RESPUESTA IA
    # =====================================================

    @staticmethod
    def validate_response(response):

        if response is None:
            return False, "La IA no respondió."

        if not isinstance(response, dict):
            return False, "Respuesta inválida."

        if not response.get("success"):
            return (
                False,
                response.get(
                    "error",
                    "Error desconocido."
                )
            )

        content = response.get(
            "content",
            ""
        )

        if not isinstance(content, str):
            content = str(content)

        content = content.strip()

        if content == "":
            return False, "La IA no devolvió contenido."

        return True, content

    # =====================================================
    # CONSTRUIR RESPUESTA
    # =====================================================

    @staticmethod
    def build_response(context, content):

        return {

            "success": True,

            "generated_at": datetime.now().strftime(
                "%d-%m-%Y %H:%M"
            ),

            "curso": context["curso"],

            "asignatura": context["asignatura"],

            "unidad": context["unidad"],

            "tema": context["tema"],

            "content": content,

            "metadata": {

                "curso": context["curso"],

                "asignatura": context["asignatura"],

                "unidad": context["unidad"],

                "tema": context["tema"],

                "duracion": context["duracion"],

                "tipo": context["tipo"],

                "metodologia": context["metodologia"],

                "evaluacion": context["evaluacion"]

            }

        }
    # =====================================================
    # LOG DE GENERACIÓN
    # =====================================================

    @staticmethod
    def log_generation(context):

        logger.info("=" * 60)
        logger.info("AulaMind Enterprise - Generación IA")
        logger.info("=" * 60)
        logger.info("Curso      : %s", context["curso"])
        logger.info("Asignatura : %s", context["asignatura"])
        logger.info("Unidad     : %s", context["unidad"])
        logger.info("Tema       : %s", context["tema"])
        logger.info("Duración   : %s", context["duracion"])
        logger.info("Tipo       : %s", context["tipo"])
        logger.info("=" * 60)

    # =====================================================
    # GENERAR PLANIFICACIÓN
    # =====================================================

    def generate(self, data):

        try:

            data = self.sanitize(data)

            valid, message = self.validate(data)

            if not valid:
                return {
                    "success": False,
                    "error": message
                }

            context = self.build_context(data)

            objectives = self.format_objectives(
                context["objetivos"]
            )

            prompt = self.build_prompt(
                context,
                objectives
            )

            prompt = self.enrich_prompt(prompt)

            self.log_generation(context)

            response = self.ai.generate(

                system_prompt="""
Eres AulaMind Enterprise 3.0.

Especialista en planificación curricular del
Ministerio de Educación de Chile.

Responde únicamente en español.

No inventes Objetivos de Aprendizaje.

Respeta exactamente el currículo entregado.
""",

                user_prompt=prompt

            )

            ok, result = self.validate_response(response)

            if not ok:
                return {
                    "success": False,
                    "error": result
                }

            return self.build_response(
                context,
                result
            )

        except Exception as e:

            logger.exception(
                "Error PlanningService.generate()"
            )

            return {
                "success": False,
                "error": str(e)
            }

    # =====================================================
    # VISTA PREVIA
    # =====================================================

    def preview(self, data):

        data = self.sanitize(data)

        context = self.build_context(data)

        objectives = self.format_objectives(
            context["objetivos"]
        )
        return {

            "success": True,

            "preview": {

                "curso": context["curso"],

                "asignatura": context["asignatura"],

                "unidad": context["unidad"],

                "tema": context["tema"],

                "duracion": context["duracion"],

                "tipo": context["tipo"],

                "objetivos": objectives

            }

        }

    # =====================================================
    # PLANTILLA VACÍA
    # =====================================================

    @staticmethod
    def empty():

        return {

            "curso": "",

            "asignatura": "",

            "unidad": "",

            "objetivo": "",

            "tema": "",

            "duracion": "90 minutos",

            "tipo": "Clase interactiva",

            "metodologia": "Aprendizaje Activo",

            "evaluacion": "Formativa",

            "recursos": "",

            "observaciones": ""

        }

    # =====================================================
    # EJEMPLO
    # =====================================================

    @staticmethod
    def sample():

        return {

            "curso": "5° Básico",

            "asignatura": "Matemática",

            "unidad": "Fracciones",

            "objetivo": [

                {

                    "code": "OA 11",

                    "description": (
                        "Resolver problemas de suma y resta "
                        "de fracciones."
                    )

                }

            ],

            "tema": "Suma y resta de fracciones",

            "duracion": "90 minutos",

            "tipo": "Clase interactiva",

            "metodologia": "Aprendizaje Basado en Problemas",

            "evaluacion": "Formativa",

            "recursos": (
                "Pizarra, guía de trabajo, "
                "material concreto."
            ),

            "observaciones": ""

        }

    # =====================================================
    # ESTADO DEL SERVICIO
    # =====================================================

    def health(self):

        return {

            "service": "PlanningService",

            "version": "3.0",

            "status": "OK",

            "openai": self.ai.available()

        }


# =====================================================
# INSTANCIA GLOBAL
# =====================================================

planning_service = PlanningService()


# =====================================================
# EXPORTACIÓN
# =====================================================

__all__ = [

    "PlanningService",

    "planning_service"

]
