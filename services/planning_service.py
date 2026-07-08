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

        required = [

            "curso",
            "asignatura",
            "unidad",
            "objetivos",
            "tema"

        ]

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

        for key, value in data.items():

            if value is None:

                result[key] = ""

                continue

            if isinstance(value, list):

                result[key] = [

                    str(item).strip()

                    for item in value

                    if str(item).strip()

                ]

            else:

                result[key] = str(value).strip()

        return result

    # =====================================================
    # CONTEXTO
    # =====================================================

    @staticmethod
    def build_context(data):

        return {

            "curso": data.get("curso", ""),

            "asignatura": data.get("asignatura", ""),

            "unidad": data.get("unidad", ""),

            "objetivos": data.get(
                "objetivos",
                data.get("objetivo", [])
            ),

            "tema": data.get("tema", ""),

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

                description = item.get(
                    "description",
                    ""
                )

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

            return False, response.get(

                "error",

                "Error desconocido."

            )

        content = response.get(

            "content",

            ""

        ).strip()

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

            "content": content

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

        # ------------------------------------------
        # Sanitizar
        # ------------------------------------------

        data = self.sanitize(data)

        # ------------------------------------------
        # Validar
        # ------------------------------------------

        valid, message = self.validate(data)

        if not valid:

            return {

                "success": False,

                "error": message

            }

        # ------------------------------------------
        # Construir contexto
        # ------------------------------------------

        context = self.build_context(data)

        # ------------------------------------------
        # Formatear OA
        # ------------------------------------------

        objectives = self.format_objectives(

            context["objetivos"]

        )

        # ------------------------------------------
        # Construir Prompt
        # ------------------------------------------

        prompt = self.build_prompt(

            context,

            objectives

        )

        # ------------------------------------------
        # Enriquecer Prompt
        # ------------------------------------------

        prompt = self.enrich_prompt(

            prompt

        )

        # ------------------------------------------
        # Registrar generación
        # ------------------------------------------

        self.log_generation(

            context

        )

        # ------------------------------------------
        # Llamar OpenAI
        # ------------------------------------------

        response = self.ai.generate(

            system_prompt="""
Eres AulaMind Enterprise.

Especialista en planificación curricular del
Ministerio de Educación de Chile.

Responde únicamente en español.

No inventes Objetivos de Aprendizaje.

Respeta siempre la información curricular entregada.

Genera documentos profesionales,
claros y pedagógicos.
""",

            user_prompt=prompt

        )

        # ------------------------------------------
        # Validar respuesta
        # ------------------------------------------

        ok, result = self.validate_response(

            response

        )

        if not ok:

            return {

                "success": False,

                "error": result

            }

        # ------------------------------------------
        # Construir respuesta
        # ------------------------------------------

        return self.build_response(

            context,

            result

        )
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

                    "description": "Resolver problemas de suma y resta de fracciones."

                }

            ],

            "tema": "Suma y resta de fracciones",

            "duracion": "90 minutos",

            "tipo": "Clase interactiva",

            "metodologia": "Aprendizaje Basado en Problemas",

            "evaluacion": "Formativa",

            "recursos": "Pizarra, guía de trabajo, material concreto.",

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
