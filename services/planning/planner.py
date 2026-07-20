"""
===========================================================
AulaMind Enterprise 3.0

Planning Engine 4.0
Orquestador

Semana 4.1H
===========================================================
"""

from __future__ import annotations

from copy import deepcopy

from services.curriculum_engine_v4 import curriculum_engine_v4

from services.planning.didactics import didactic_engine
from services.planning.evaluations import evaluation_engine
from services.planning.resources import resources_engine
from services.planning.dua import dua_engine
from services.planning.indicators import indicators_engine
from services.planning.prompt_builder import prompt_builder


class PlanningEngine:
    """
    Planning Engine 4.0

    Este motor coordina todos los componentes del sistema
    de planificación.

    No contiene lógica didáctica.

    Su única responsabilidad es orquestar los motores.
    """

    def __init__(self):

        self.curriculum = curriculum_engine_v4

        self.didactics = didactic_engine

        self.evaluation = evaluation_engine

        self.resources = resources_engine

        self.dua = dua_engine

        self.indicators = indicators_engine

        self.prompt_builder = prompt_builder

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

        curriculum = deepcopy(record)

        didactics = self.didactics.generate(
            curriculum
        )

        evaluation = self.evaluation.generate(
            curriculum
        )

        resources = self.resources.generate(
            curriculum
        )

        dua = self.dua.generate(
            curriculum
        )

        indicators = self.indicators.generate(
            curriculum
        )

        prompt = self.prompt_builder.build(

            curriculum=curriculum,

            didactics=didactics,

            evaluation=evaluation,

            resources=resources,

            dua=dua,

            indicators=indicators,

        )

        return {

            "curriculum": curriculum,

            "didactics": didactics,

            "evaluation": evaluation,

            "resources": resources,

            "dua": dua,

            "indicators": indicators,

            "prompt": prompt,

            "metadata": {

                "modalidad":
                    curriculum.get("modalidad"),

                "curso":
                    curriculum.get("curso"),

                "asignatura":
                    curriculum.get("asignatura"),

                "engine":
                    "Planning Engine 4.0",

            }

        }
            # ---------------------------------------------------------

    def statistics(self):

        curriculum_stats = self.curriculum.statistics()

        return {

            "engine": "Planning Engine 4.0",

            "version": "Semana 4.1H",

            "curriculum_documents":
                curriculum_stats.get(
                    "documentos_adaptados",
                    0,
                ),

            "modalidades":
                curriculum_stats.get(
                    "modalidades",
                    0,
                ),

            "cursos":
                curriculum_stats.get(
                    "cursos",
                    0,
                ),

            "asignaturas":
                curriculum_stats.get(
                    "asignaturas",
                    0,
                ),

            "unidades":
                curriculum_stats.get(
                    "unidades",
                    0,
                ),

            "oa":
                curriculum_stats.get(
                    "oa",
                    0,
                ),

            "planning_modules": {

                "didactics": True,

                "evaluation": True,

                "resources": True,

                "dua": True,

                "indicators": True,

                "prompt_builder": True,

            }

        }


# =========================================================
# Instancia global
# =========================================================

planning_engine = PlanningEngine()