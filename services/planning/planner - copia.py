"""
===========================================================
AulaMind Enterprise 3.0

Planning Engine 4.0
===========================================================
"""

from __future__ import annotations

from copy import deepcopy

from services.curriculum_engine_v4 import curriculum_engine_v4


class PlanningEngine:
    """
    Motor base de planificación.

    Esta primera versión solamente obtiene la información
    curricular desde CurriculumEngineV4.

    Los siguientes bloques incorporarán:

        • Inicio
        • Desarrollo
        • Cierre
        • Evaluación
        • DUA
        • Recursos
        • Instrumentos
        • IA Prompt
    """

    def __init__(self):

        self.curriculum = curriculum_engine_v4

    # ---------------------------------------------------------

    def generate(
        self,
        modalidad: str,
        curso: str,
        asignatura: str,
    ) -> dict | None:

        record = self.curriculum.record(
            modalidad,
            curso,
            asignatura,
        )

        if record is None:

            return None

        return {

            "curriculum": deepcopy(record),

            "planning": {

                "inicio": "",

                "desarrollo": "",

                "cierre": "",

                "evaluacion_formativa": "",

                "recursos": [],

                "dua": [],

                "adecuaciones": [],

                "indicadores": [],

                "instrumento": "",

                "evidencias": [],

                "ia_prompt": ""

            }

        }

    # ---------------------------------------------------------

    def statistics(self):

        return {

            "engine": "Planning Engine 4.0",

            "curriculum_documents":

                self.curriculum.statistics()[
                    "documentos_adaptados"
                ],

            "modalidades":

                self.curriculum.statistics()[
                    "modalidades"
                ]

        }