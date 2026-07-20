"""
===========================================================
AulaMind Enterprise 3.0

Curriculum Validator

Reference Checker

Semana 5A.4
===========================================================
"""

from __future__ import annotations

from typing import Any

from .models import (
    ValidationResult,
    ValidationStatus,
)


class ReferenceChecker:
    """
    Verifica que un documento curricular posea la
    información mínima de referencia.

    Este módulo NO valida el esquema ni detecta
    duplicados.

    Solamente determina si existen suficientes
    antecedentes curriculares para generar
    planificaciones confiables.
    """

    OPTIONAL_REFERENCE_FIELDS = [

        "nivel",

        "fuente",

        "marco",

        "estado_curricular",

    ]

    # ---------------------------------------------------------

    def validate(
        self,
        path: str,
        data: dict[str, Any],
    ) -> ValidationResult:

        result = ValidationResult(path=path)

        if not isinstance(data, dict):

            result.set_status(
                ValidationStatus.STRUCTURAL
            )

            result.add_error(

                "ROOT_TYPE",

                "El documento raíz no es un objeto JSON.",

            )

            return result

        result.modalidad = str(
            data.get("modalidad", "")
        )

        result.curso = str(
            data.get("curso", "")
        )

        result.asignatura = str(
            data.get("asignatura", "")
        )

        missing = []

        for field in self.OPTIONAL_REFERENCE_FIELDS:

            value = data.get(field)

            if value in (None, "", [], {}):

                missing.append(field)

                result.add_warning(

                    "REFERENCE",

                    f"No se encontró '{field}'."

                )

        result.metadata["missing_reference_fields"] = missing

        if len(missing) >= 2:

            result.set_status(

                ValidationStatus.REFERENCE_REQUIRED

            )

        return result

    # ---------------------------------------------------------

    def statistics(self):

        return {

            "validator":
                "Reference Checker",

            "version":
                "Semana 5A.4",

            "reference_fields":
                len(self.OPTIONAL_REFERENCE_FIELDS),

        }


reference_checker = ReferenceChecker()