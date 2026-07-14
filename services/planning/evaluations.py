"""
===========================================================
AulaMind Enterprise 3.0

Planning Engine 4.0
Evaluation Engine

Generación automática de evaluaciones e instrumentos.

Versión: Semana 4.1C
===========================================================
"""

from __future__ import annotations

from copy import deepcopy


class EvaluationEngine:
    """
    Motor de evaluación.

    Genera automáticamente los elementos básicos de evaluación
    a partir del registro curricular entregado por el
    CurriculumEngineV4.

    En futuras versiones incorporará IA para personalizar
    los instrumentos según nivel, asignatura y metodología.
    """

    # ---------------------------------------------------------

    def generate(
        self,
        curriculum: dict,
    ) -> dict:

        curriculum = deepcopy(curriculum)

        unidades = curriculum.get("unidades", [])

        unidad = unidades[0] if unidades else {}

        oa = unidad.get("oa", [])

        return {

            "diagnostica": self.build_diagnostica(oa),

            "formativa": self.build_formativa(oa),

            "sumativa": self.build_sumativa(oa),

            "instrumentos": self.build_instrumentos(oa),

            "ticket_salida": self.build_ticket(oa)

        }

    # ---------------------------------------------------------

    def build_diagnostica(
        self,
        oa,
    ):

        return {

            "objetivo":

                "Identificar conocimientos previos de los estudiantes.",

            "preguntas": [

                "¿Qué sabes sobre este tema?",

                "¿Dónde lo has utilizado anteriormente?",

                "¿Qué dudas tienes antes de comenzar?"

            ]

        }

    # ---------------------------------------------------------

    def build_formativa(
        self,
        oa,
    ):

        indicadores = []

        if oa:

            for objetivo in oa:

                if isinstance(objetivo, dict):

                    descripcion = objetivo.get(
                        "descripcion",
                        ""
                    )

                else:

                    descripcion = str(objetivo)

                indicadores.append({

                    "indicador":
                        descripcion,

                    "logrado":
                        False

                })

        if not indicadores:

            indicadores.append({

                "indicador":
                    "Participa activamente en las actividades propuestas.",

                "logrado":
                    False

            })

        return {

            "tipo":
                "Evaluación Formativa",

            "indicadores":
                indicadores

        }

    # ---------------------------------------------------------

    def build_sumativa(
        self,
        oa,
    ):

        return {

            "tipo":

                "Evaluación Sumativa",

            "descripcion":

                "Actividad final de aplicación de los aprendizajes.",

            "ponderacion":

                100

        }

    # ---------------------------------------------------------

    def build_instrumentos(
        self,
        oa,
    ):

        return [

            {

                "nombre":
                    "Lista de Cotejo",

                "descripcion":
                    "Verificación del logro de indicadores."

            },

            {

                "nombre":
                    "Escala de Apreciación",

                "descripcion":
                    "Valoración del desempeño observado."

            },

            {

                "nombre":
                    "Rúbrica",

                "descripcion":
                    "Evaluación mediante niveles de desempeño."

            }

        ]

    # ---------------------------------------------------------

    def build_ticket(
        self,
        oa,
    ):

        return {

            "titulo":

                "Ticket de Salida",

            "preguntas": [

                "¿Qué aprendiste hoy?",

                "¿Qué fue lo más difícil?",

                "¿Qué necesitas reforzar?"

            ]

        }

    # ---------------------------------------------------------

    def statistics(self):

        return {

            "engine":
                "Evaluation Engine 4.0",

            "version":
                "Semana 4.1C"

        }


evaluation_engine = EvaluationEngine()