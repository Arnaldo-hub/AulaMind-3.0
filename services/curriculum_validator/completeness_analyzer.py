"""
===========================================================
AulaMind Enterprise 3.0

Curriculum Validator

Completeness Analyzer

Semana 5B.2
===========================================================
"""

from __future__ import annotations

from typing import Any


class CompletenessAnalyzer:
    """
    Calcula el porcentaje de completitud
    de un documento curricular.
    """

    REQUIRED_FIELDS = (

        "modalidad",

        "nivel",

        "curso",

        "asignatura",

        "unidades",

        "fuente",

        "marco",

        "estado_curricular",

    )

    # ---------------------------------------------------------

    def analyze(
        self,
        data: dict[str, Any],
    ) -> dict:

        result = {

            "score": 0,

            "completed": 0,

            "required": len(self.REQUIRED_FIELDS),

            "missing": [],

            "warnings": [],

        }

        if not isinstance(data, dict):

            result["warnings"].append(
                "Documento no válido."
            )

            return result

        completed = 0

        # -------------------------------------------------
        # Campos obligatorios
        # -------------------------------------------------

        for field in self.REQUIRED_FIELDS:

            value = data.get(field)

            if self._has_value(value):

                completed += 1

            else:

                result["missing"].append(field)

        # -------------------------------------------------
        # Unidades
        # -------------------------------------------------

        units = data.get("unidades", [])

        if isinstance(units, list):

            if not units:

                result["warnings"].append(
                    "Documento sin unidades."
                )

            else:

                empty_oa = 0

                for unit in units:

                    oa = unit.get("oa", [])

                    if not oa:

                        empty_oa += 1

                if empty_oa:

                    result["warnings"].append(
                        f"{empty_oa} unidades sin OA."
                    )

        # -------------------------------------------------

        score = round(
            completed * 100 / len(self.REQUIRED_FIELDS),
            2,
        )

        result["completed"] = completed

        result["score"] = score

        return result

    # ---------------------------------------------------------

    @staticmethod
    def _has_value(value):

        if value is None:
            return False

        if isinstance(value, str):

            return value.strip() != ""

        if isinstance(value, list):

            return len(value) > 0

        return True

    # ---------------------------------------------------------

    def statistics(self):

        return {

            "module": "Completeness Analyzer",

            "version": "5B.2",

            "required_fields": len(self.REQUIRED_FIELDS),

        }


completeness_analyzer = CompletenessAnalyzer()