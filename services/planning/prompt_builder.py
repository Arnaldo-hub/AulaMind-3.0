"""
===========================================================
AulaMind Enterprise 3.0

Planning Engine 4.0
Prompt Builder

Construye el Prompt Maestro para la IA utilizando la
información generada por todos los motores.

Semana 4.1G
===========================================================
"""

from __future__ import annotations


class PromptBuilder:
    """
    Constructor del Prompt Maestro.

    No genera planificación.

    Su única responsabilidad es convertir toda la
    información del Planning Engine en un contexto
    estructurado para la IA.
    """

    # ---------------------------------------------------------

    def build(
        self,
        curriculum: dict,
        didactics: dict,
        evaluation: dict,
        resources: dict,
        dua: dict,
        indicators: dict,
    ) -> str:

        lines = []

        lines.append(
            "Eres un docente experto del Currículum Nacional de Chile."
        )

        lines.append("")
        lines.append("=== CONTEXTO CURRICULAR ===")

        lines.append(
            f"Modalidad: {curriculum.get('modalidad','')}"
        )

        lines.append(
            f"Curso: {curriculum.get('curso','')}"
        )

        lines.append(
            f"Asignatura: {curriculum.get('asignatura','')}"
        )

        unidades = curriculum.get("unidades", [])

        if unidades:

            unidad = unidades[0]

            lines.append(
                f"Unidad: {unidad.get('nombre','')}"
            )

        lines.append("")

        lines.append("=== PLANIFICACIÓN DIDÁCTICA ===")

        for item in didactics.get("inicio", []):

            lines.append(
                f"- Inicio: {item.get('descripcion','')}"
            )

        for item in didactics.get("desarrollo", []):

            lines.append(
                f"- Desarrollo: {item.get('descripcion','')}"
            )

        for item in didactics.get("cierre", []):

            lines.append(
                f"- Cierre: {item.get('descripcion','')}"
            )

        lines.append("")
        lines.append("=== EVALUACIÓN ===")

        formativa = evaluation.get(
            "formativa",
            {}
        )

        for item in formativa.get(
            "indicadores",
            []
        ):

            lines.append(
                f"- {item.get('indicador','')}"
            )

        lines.append("")
        lines.append("=== RECURSOS ===")

        for item in resources.get(
            "material_concreto",
            []
        ):

            lines.append(
                f"- {item}"
            )

        lines.append("")
        lines.append("=== DUA ===")

        for item in dua.get(
            "principio1",
            []
        ):

            lines.append(
                f"- {item}"
            )

        lines.append("")
        lines.append("=== INDICADORES ===")

        for item in indicators.get(
            "criterios_exito",
            []
        ):

            lines.append(
                f"- {item}"
            )

        lines.append("")
        lines.append(
            "Con toda esta información genera una planificación"
        )

        lines.append(
            "completa, alineada al Currículum Nacional de Chile."
        )

        return "\n".join(lines)

    # ---------------------------------------------------------

    def statistics(self):

        return {

            "engine":
                "Prompt Builder 4.0",

            "version":
                "Semana 4.1G"

        }


prompt_builder = PromptBuilder()