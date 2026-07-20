"""
===========================================================
AulaMind Enterprise 3.0

Curriculum Validator

Duplicate Detector

Semana 5A.8B
===========================================================
"""

from __future__ import annotations

from typing import Any

from .models import (
    ValidationResult,
    ValidationStatus,
)


class DuplicateDetector:
    """
    Detector de documentos duplicados.

    Un documento solamente puede participar en la
    detección de duplicados cuando posee al menos:

        - curso
        - asignatura

    Esto evita falsos positivos en documentos de
    auditoría, inventarios o estructuras auxiliares.
    """

    # ---------------------------------------------------------

    def __init__(self):

        self._keys: dict[str, str] = {}

    # ---------------------------------------------------------

    def reset(self):

        self._keys.clear()

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

        key = self.build_key(data)

        result.metadata["duplicate_key"] = key

        # Sin clave curricular no se puede
        # detectar duplicados.
        if not key:
            return result

        if key in self._keys:

            previous = self._keys[key]

            result.set_status(
                ValidationStatus.DUPLICATE
            )

            result.add_error(
                "DUPLICATE",
                f"Documento duplicado de '{previous}'.",
            )

            return result

        self._keys[key] = path

        return result
            # ---------------------------------------------------------

    def build_key(
        self,
        data: dict[str, Any],
    ) -> str:
        """
        Construye una clave curricular estable.

        Solo se consideran documentos que poseen
        al menos curso y asignatura.
        """

        curso = self._normalize(
            data.get("curso")
        )

        asignatura = self._normalize(
            data.get("asignatura")
        )

        if not curso or not asignatura:
            return ""

        values = [

            self._normalize(
                data.get("modalidad")
            ),

            curso,

            asignatura,

        ]

        nivel = self._normalize(
            data.get("nivel")
        )

        if nivel:
            values.append(nivel)

        return "|".join(values)

    # ---------------------------------------------------------

    @staticmethod
    def _normalize(value) -> str:

        if value is None:
            return ""

        return str(value).strip().lower()

    # ---------------------------------------------------------

    def statistics(self):

        return {

            "validator":
                "Duplicate Detector",

            "version":
                "Semana 5A.8B",

            "registered_keys":
                len(self._keys),

        }


duplicate_detector = DuplicateDetector()