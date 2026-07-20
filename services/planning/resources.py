"""
===========================================================
AulaMind Enterprise 3.0

Planning Engine 4.0
Resources Engine

Generación automática de recursos didácticos.

Semana 4.1D
===========================================================
"""

from __future__ import annotations

from copy import deepcopy


class ResourcesEngine:
    """
    Motor de recursos didácticos.

    Genera automáticamente los recursos sugeridos para una
    planificación utilizando la información curricular.

    Versiones futuras:

        • Recursos MINEDUC
        • Recursos IA
        • Recursos por OA
        • Recursos por asignatura
        • Recursos descargables
    """

    # ---------------------------------------------------------

    def generate(
        self,
        curriculum: dict,
    ) -> dict:

        curriculum = deepcopy(curriculum)

        asignatura = curriculum.get(
            "asignatura",
            "",
        )

        curso = curriculum.get(
            "curso",
            "",
        )

        modalidad = curriculum.get(
            "modalidad",
            "",
        )

        return {

            "material_concreto":
                self.material_concreto(
                    asignatura
                ),

            "recursos_digitales":
                self.recursos_digitales(
                    asignatura
                ),

            "tic":
                self.tic(
                    asignatura
                ),

            "bibliografia":
                self.bibliografia(
                    asignatura
                ),

            "material_imprimible":
                self.material_imprimible(
                    asignatura
                ),

            "inclusion":
                self.inclusion(),

            "metadata": {

                "modalidad":
                    modalidad,

                "curso":
                    curso,

                "asignatura":
                    asignatura,

            }

        }

    # ---------------------------------------------------------

    def material_concreto(
        self,
        asignatura: str,
    ):

        comunes = [

            "Pizarra",

            "Plumones",

            "Guía impresa",

            "Cuaderno",

            "Lápiz",

        ]

        asignatura = asignatura.lower()

        if "matem" in asignatura:

            comunes.extend([

                "Material Base 10",

                "Regla",

                "Geoplano",

            ])

        elif "ciencias" in asignatura:

            comunes.extend([

                "Material de laboratorio",

                "Lupa",

                "Recipientes",

            ])

        elif "lenguaje" in asignatura:

            comunes.extend([

                "Textos de lectura",

                "Diccionario",

            ])

        return comunes

    # ---------------------------------------------------------

    def recursos_digitales(
        self,
        asignatura: str,
    ):

        return [

            {

                "nombre":
                    "Currículum Nacional",

                "tipo":
                    "Portal"

            },

            {

                "nombre":
                    "Presentación digital",

                "tipo":
                    "PPT"

            },

            {

                "nombre":
                    "Video educativo",

                "tipo":
                    "Video"

            }

        ]

    # ---------------------------------------------------------

    def tic(
        self,
        asignatura: str,
    ):

        return [

            "Computador",

            "Proyector",

            "Internet",

            "Plataforma AulaMind",

        ]

    # ---------------------------------------------------------

    def bibliografia(
        self,
        asignatura: str,
    ):

        return [

            {

                "titulo":

                    "Bases Curriculares MINEDUC"

            },

            {

                "titulo":

                    "Programa de Estudio"

            }

        ]

    # ---------------------------------------------------------

    def material_imprimible(
        self,
        asignatura: str,
    ):

        return [

            "Guía de trabajo",

            "Lista de cotejo",

            "Rúbrica",

            "Ticket de salida",

        ]

    # ---------------------------------------------------------

    def inclusion(
        self,
    ):

        return [

            "Material con letra ampliada",

            "Apoyos visuales",

            "Instrucciones paso a paso",

            "Trabajo colaborativo",

        ]

    # ---------------------------------------------------------

    def statistics(
        self,
    ):

        return {

            "engine":

                "Resources Engine 4.0",

            "version":

                "Semana 4.1D",

        }


resources_engine = ResourcesEngine()