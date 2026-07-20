"""
===========================================================
AulaMind Enterprise 3.0

Curriculum Validator

Schema Validator

Semana 5A.2
===========================================================
"""

from __future__ import annotations

from typing import Any

from .models import (
    ValidationResult,
    ValidationStatus,
)


class SchemaValidator:
    """
    Valida la estructura mínima de un documento curricular.

    Este módulo NO verifica duplicados,
    referencias ni cobertura.

    Solamente responde la pregunta:

        ¿El JSON posee la estructura mínima
        para poder ser procesado?
    """

    REQUIRED_ROOT_FIELDS = [

        "curso",

        "asignatura",

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

                "El documento raíz debe ser un objeto JSON.",

            )

            return result

        self._load_metadata(
            result,
            data,
        )

        self._validate_required_fields(
            result,
            data,
        )

        self._validate_units(
            result,
            data,
        )

        if result.errores:

            if result.estado == ValidationStatus.VALID:

                result.set_status(
                    ValidationStatus.SCHEMA_ERROR
                )

        return result

    # ---------------------------------------------------------

    def _load_metadata(
        self,
        result,
        data,
    ):

        result.modalidad = str(
            data.get("modalidad", "")
        )

        result.curso = str(
            data.get("curso", "")
        )

        result.asignatura = str(
            data.get("asignatura", "")
        )

    # ---------------------------------------------------------

    def _validate_required_fields(
        self,
        result,
        data,
    ):

        for field in self.REQUIRED_ROOT_FIELDS:

            if field not in data:

                result.add_error(

                    "MISSING_FIELD",

                    f"Falta el campo '{field}'.",

                )

            elif data[field] in (

                None,

                "",

            ):

                result.add_error(

                    "EMPTY_FIELD",

                    f"El campo '{field}' está vacío.",

                )

    # ---------------------------------------------------------

    def _validate_units(
        self,
        result,
        data,
    ):

        units = data.get("unidades")

        if units is None:

            result.add_warning(

                "NO_UNITS",

                "El documento no posee unidades.",

            )

            result.set_status(
                ValidationStatus.INCOMPLETE
            )

            return

        if not isinstance(units, list):

            result.add_error(

                "UNITS_TYPE",

                "'unidades' debe ser una lista.",

            )

            return

        if len(units) == 0:

            result.add_warning(

                "EMPTY_UNITS",

                "La lista de unidades está vacía.",

            )

            result.set_status(
                ValidationStatus.INCOMPLETE
            )

            return

        for index, unit in enumerate(units):

            if not isinstance(unit, dict):

                result.add_error(

                    "UNIT_TYPE",

                    f"La unidad {index+1} no es un objeto.",

                )

                continue

            if "nombre" not in unit:

                result.add_warning(

                    "UNIT_NAME",

                    f"La unidad {index+1} no posee nombre.",

                )

            if "oa" not in unit:

                result.add_warning(

                    "UNIT_OA",

                    f"La unidad {index+1} no posee OA.",

                )

    # ---------------------------------------------------------

    def statistics(self):

        return {

            "validator":

                "Schema Validator",

            "version":

                "Semana 5A.2",

            "required_fields":

                len(self.REQUIRED_ROOT_FIELDS),

        }


schema_validator = SchemaValidator()