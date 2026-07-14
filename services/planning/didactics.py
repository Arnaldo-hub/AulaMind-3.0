"""
===========================================================
AulaMind Enterprise 3.0

Planning Engine 4.0
Didactic Engine

Genera automáticamente la estructura didáctica
de una clase utilizando la información curricular.

Versión: Semana 4.1B
===========================================================
"""

from __future__ import annotations

from copy import deepcopy


class DidacticEngine:
    """
    Motor de generación didáctica.

    Esta primera versión construye la estructura base
    de una planificación utilizando la información
    curricular entregada por CurriculumEngine.

    En versiones posteriores incorporará:

        • ABP
        • Aula invertida
        • Aprendizaje colaborativo
        • Aprendizaje basado en proyectos
        • IA personalizada
    """

    # ---------------------------------------------------------

    def generate(
        self,
        curriculum: dict,
        duration: int = 90,
        methodology: str = "tradicional",
    ) -> dict:

        curriculum = deepcopy(curriculum)

        unidades = curriculum.get("unidades", [])

        unidad = unidades[0] if unidades else {}

        oa = unidad.get("oa", [])

        return {

            "duracion": duration,

            "metodologia": methodology,

            "inicio": self.build_inicio(
                curriculum,
                unidad,
                oa,
            ),

            "desarrollo": self.build_desarrollo(
                curriculum,
                unidad,
                oa,
            ),

            "cierre": self.build_cierre(
                curriculum,
                unidad,
                oa,
            ),

        }

    # ---------------------------------------------------------

    def build_inicio(
        self,
        curriculum,
        unidad,
        oa,
    ):

        actividades = [

            {
                "titulo":
                    "Activación de conocimientos previos",

                "descripcion":
                    (
                        "El docente inicia la clase "
                        "recuperando los conocimientos "
                        "previos mediante preguntas, "
                        "conversación guiada o lluvia de ideas."
                    ),

                "duracion": 10,
            },

            {
                "titulo":
                    "Presentación del objetivo",

                "descripcion":
                    (
                        "Se comunica el propósito de "
                        "aprendizaje y los criterios "
                        "de éxito de la clase."
                    ),

                "duracion": 5,
            }

        ]

        return actividades

    # ---------------------------------------------------------

    def build_desarrollo(
        self,
        curriculum,
        unidad,
        oa,
    ):

        actividades = []

        if oa:

            for objetivo in oa:

                descripcion = ""

                if isinstance(objetivo, dict):

                    descripcion = objetivo.get(
                        "descripcion",
                        ""
                    )

                else:

                    descripcion = str(objetivo)

                actividades.append(

                    {

                        "titulo":
                            "Actividad de Aprendizaje",

                        "descripcion":
                            descripcion,

                        "duracion": 15,

                    }

                )

        if not actividades:

            actividades.append(

                {

                    "titulo":
                        "Actividad Principal",

                    "descripcion":
                        (
                            "Desarrollar actividades "
                            "relacionadas con los "
                            "objetivos de aprendizaje "
                            "de la unidad."
                        ),

                    "duracion": 40,

                }

            )

        return actividades

    # ---------------------------------------------------------

    def build_cierre(
        self,
        curriculum,
        unidad,
        oa,
    ):

        actividades = [

            {

                "titulo":
                    "Metacognición",

                "descripcion":
                    (
                        "Los estudiantes reflexionan "
                        "sobre lo aprendido durante "
                        "la clase."
                    ),

                "duracion": 10,

            },

            {

                "titulo":
                    "Ticket de salida",

                "descripcion":
                    (
                        "Cada estudiante responde "
                        "una pregunta breve para "
                        "evidenciar el aprendizaje."
                    ),

                "duracion": 5,

            }

        ]

        return actividades

    # ---------------------------------------------------------

    def statistics(self):

        return {

            "engine":
                "Didactic Engine 4.0",

            "version":
                "Semana 4.1B",

        }


didactic_engine = DidacticEngine()