"""
===========================================================
AulaMind Enterprise 3.0

Planning Engine 4.0
Indicators Engine

Generación automática de:

• Indicadores de logro
• Criterios de éxito
• Evidencias
• Habilidades
• Actitudes

Semana 4.1F
===========================================================
"""

from __future__ import annotations

from copy import deepcopy


class IndicatorsEngine:
    """
    Motor de indicadores.

    Construye los indicadores básicos utilizando la
    información curricular obtenida desde CurriculumEngine.

    En futuras versiones estos indicadores podrán ser
    enriquecidos mediante IA y por OA específico.
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

            "indicadores":
                self.indicadores(oa),

            "criterios_exito":
                self.criterios_exito(oa),

            "evidencias":
                self.evidencias(oa),

            "habilidades":
                self.habilidades(curriculum),

            "actitudes":
                self.actitudes(curriculum),

        }

    # ---------------------------------------------------------

    def indicadores(
        self,
        oa,
    ):

        resultado = []

        if oa:

            for objetivo in oa:

                if isinstance(objetivo, dict):

                    descripcion = objetivo.get(
                        "descripcion",
                        ""
                    )

                else:

                    descripcion = str(objetivo)

                resultado.append({

                    "descripcion":
                        descripcion,

                    "estado":
                        "pendiente"

                })

        if not resultado:

            resultado.append({

                "descripcion":
                    "Participa en las actividades propuestas.",

                "estado":
                    "pendiente"

            })

        return resultado

    # ---------------------------------------------------------

    def criterios_exito(
        self,
        oa,
    ):

        return [

            "Comprende el objetivo de aprendizaje.",

            "Aplica correctamente los procedimientos.",

            "Argumenta sus respuestas.",

            "Participa activamente.",

            "Comunica sus aprendizajes."

        ]

    # ---------------------------------------------------------

    def evidencias(
        self,
        oa,
    ):

        return [

            "Guía desarrollada.",

            "Actividad práctica.",

            "Registro de observación.",

            "Ticket de salida.",

            "Producto final."

        ]

    # ---------------------------------------------------------

    def habilidades(
        self,
        curriculum,
    ):

        return [

            "Pensamiento crítico",

            "Resolución de problemas",

            "Comunicación",

            "Trabajo colaborativo",

            "Creatividad"

        ]

    # ---------------------------------------------------------

    def actitudes(
        self,
        curriculum,
    ):

        return [

            "Respeto",

            "Responsabilidad",

            "Autonomía",

            "Perseverancia",

            "Participación"

        ]

    # ---------------------------------------------------------

    def statistics(self):

        return {

            "engine":
                "Indicators Engine 4.0",

            "version":
                "Semana 4.1F"

        }


indicators_engine = IndicatorsEngine()