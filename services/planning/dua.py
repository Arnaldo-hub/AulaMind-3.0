"""
===========================================================
AulaMind Enterprise 3.0

Planning Engine 4.0
DUA Engine

Diseño Universal para el Aprendizaje (DUA)

Semana 4.1E
===========================================================
"""

from __future__ import annotations

from copy import deepcopy


class DUAEngine:
    """
    Motor DUA.

    Genera recomendaciones de:

        • Principio I
        • Principio II
        • Principio III
        • Adecuaciones Curriculares
        • Apoyos

    En versiones futuras incorporará:

        • Adaptaciones por diagnóstico
        • IA personalizada
        • Perfil del estudiante
    """

    # -----------------------------------------------------

    def generate(
        self,
        curriculum: dict,
    ) -> dict:

        curriculum = deepcopy(curriculum)

        return {

            "principio1":
                self.principio1(curriculum),

            "principio2":
                self.principio2(curriculum),

            "principio3":
                self.principio3(curriculum),

            "adecuaciones":
                self.adecuaciones(curriculum),

            "apoyos":
                self.apoyos(curriculum)

        }

    # -----------------------------------------------------

    def principio1(
        self,
        curriculum,
    ):

        return [

            "Utilizar apoyos visuales.",

            "Incorporar ejemplos concretos.",

            "Relacionar el contenido con experiencias previas.",

            "Presentar información mediante imágenes y esquemas.",

            "Utilizar material manipulativo cuando corresponda."

        ]

    # -----------------------------------------------------

    def principio2(
        self,
        curriculum,
    ):

        return [

            "Permitir respuestas orales y escritas.",

            "Favorecer el trabajo colaborativo.",

            "Incorporar actividades prácticas.",

            "Utilizar herramientas digitales.",

            "Ofrecer diferentes formas de demostrar el aprendizaje."

        ]

    # -----------------------------------------------------

    def principio3(
        self,
        curriculum,
    ):

        return [

            "Plantear desafíos progresivos.",

            "Entregar retroalimentación permanente.",

            "Favorecer la autonomía.",

            "Promover la participación activa.",

            "Relacionar los aprendizajes con situaciones reales."

        ]

    # -----------------------------------------------------

    def adecuaciones(
        self,
        curriculum,
    ):

        return [

            {

                "tipo":
                    "Acceso",

                "descripcion":
                    "Aumentar tamaño de letra cuando sea necesario."

            },

            {

                "tipo":
                    "Metodológica",

                "descripcion":
                    "Entregar instrucciones paso a paso."

            },

            {

                "tipo":
                    "Evaluación",

                "descripcion":
                    "Otorgar tiempo adicional."

            },

            {

                "tipo":
                    "Participación",

                "descripcion":
                    "Favorecer tutorías entre pares."

            }

        ]

    # -----------------------------------------------------

    def apoyos(
        self,
        curriculum,
    ):

        return [

            "Apoyos visuales",

            "Material concreto",

            "Tecnologías de apoyo",

            "Organizadores gráficos",

            "Pictogramas",

            "Modelamiento del docente"

        ]

    # -----------------------------------------------------

    def statistics(self):

        return {

            "engine":
                "DUA Engine 4.0",

            "version":
                "Semana 4.1E"

        }


dua_engine = DUAEngine()
