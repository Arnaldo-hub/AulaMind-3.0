"""
===========================================================
AulaMind Enterprise 3.0
services/evaluation_service.py
-----------------------------------------------------------

Motor de Evaluaciones IA

Autor:
Biotecno Chile
===========================================================
"""

from services.openai_service import OpenAIService


class EvaluationService:
    """
    Servicio encargado de construir el prompt y solicitar
    la evaluación a OpenAI.
    """

    def __init__(self):

        self.ai = OpenAIService()

    # ======================================================
    # PROMPT DEL SISTEMA
    # ======================================================

    def _system_prompt(self):

        return """
Eres AulaMind IA, un experto en pedagogía, evaluación educativa y
currículum nacional de Chile.

Tu trabajo es crear evaluaciones profesionales para docentes.

La evaluación debe contener SIEMPRE:

1. Encabezado
2. Instrucciones para el estudiante
3. Objetivo de Aprendizaje
4. Puntaje total
5. Preguntas
6. Solucionario
7. Indicadores evaluados

Utiliza lenguaje claro.

No escribas explicaciones adicionales.

Devuelve solamente la evaluación.
"""

    # ======================================================
    # PROMPT DEL USUARIO
    # ======================================================

    def _user_prompt(self, data):

        return f"""
Genera una evaluación con la siguiente información:

Asignatura:
{data.get("asignatura")}

Curso:
{data.get("curso")}

Unidad:
{data.get("unidad")}

Objetivo de Aprendizaje:
{data.get("objetivo")}

Tema:
{data.get("tema")}

Tipo de evaluación:
{data.get("tipo")}

Cantidad de preguntas:
{data.get("preguntas")}

Nivel de dificultad:
{data.get("dificultad")}

Además incluye:

- Selección múltiple
- Verdadero y Falso
- Desarrollo
- Puntaje por pregunta
- Puntaje total
- Solucionario
- Indicadores evaluados
"""

    # ======================================================
    # GENERAR
    # ======================================================

    def generate(self, data):

        try:

            resultado = self.ai.generate(

                self._system_prompt(),

                self._user_prompt(data)

            )

            if not resultado.get("success"):

                return resultado

            return {

                "success": True,

                "content": resultado.get("content")

            }

        except Exception as e:

            return {

                "success": False,

                "error": str(e)

            }

    # ======================================================
    # PREVIEW
    # ======================================================

    def preview(self, texto):

        return {

            "success": True,

            "preview": texto

        }

    # ======================================================
    # EJEMPLO
    # ======================================================

    def sample(self):

        return {

            "success": True,

            "content": """
EVALUACIÓN DE MATEMÁTICA

Curso:
5° Básico

Unidad:
Fracciones

OA:
OA11

----------------------------------------

I. Selección múltiple

1.- ¿Cuál fracción equivale a 1/2?

A) 2/6

B) 3/6

C) 5/8

D) 7/8

----------------------------------------

II. Verdadero y Falso

2.- Dos fracciones equivalentes representan
la misma cantidad.

----------------------------------------

III. Desarrollo

3.- Resuelve:

2/5 + 1/5

----------------------------------------

Puntaje Total:

30 puntos

----------------------------------------

SOLUCIONARIO

1) B

2) Verdadero

3) 3/5
"""

        }