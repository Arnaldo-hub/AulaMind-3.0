"""
===========================================================
AulaMind Enterprise 3.0

Curriculum Validator

Coverage Report

Semana 5A.5
===========================================================
"""

from __future__ import annotations

from collections import Counter

from .models import (
    ValidationResult,
    ValidationSummary,
    ValidationStatus,
)


class CoverageReport:
    """
    Generador del informe de cobertura curricular.

    Este módulo NO valida documentos.

    Su responsabilidad es consolidar todos los
    ValidationResult obtenidos por los distintos
    validadores y producir un informe único.
    """

    # -----------------------------------------------------

    def generate(
        self,
        results: list[ValidationResult],
    ) -> ValidationSummary:

        summary = ValidationSummary()

        for result in results:

            summary.add(result)

        return summary

    # -----------------------------------------------------

    def priority_list(
        self,
        results: list[ValidationResult],
    ) -> list[ValidationResult]:

        priority = []

        order = {

            ValidationStatus.STRUCTURAL: 0,

            ValidationStatus.SCHEMA_ERROR: 1,

            ValidationStatus.DUPLICATE: 2,

            ValidationStatus.REFERENCE_REQUIRED: 3,

            ValidationStatus.INCOMPLETE: 4,

            ValidationStatus.VALID: 5,

        }

        priority.extend(results)

        priority.sort(

            key=lambda r: (

                order.get(r.estado, 99),

                r.modalidad,

                r.curso,

                r.asignatura,

            )

        )

        return priority

    # -----------------------------------------------------

    def status_counter(
        self,
        results: list[ValidationResult],
    ):

        counter = Counter()

        for result in results:

            counter[result.estado.value] += 1

        return dict(counter)

    # -----------------------------------------------------

    def to_dict(
        self,
        summary: ValidationSummary,
    ):

        return {

            "total":

                summary.total,

            "valid":

                summary.valid,

            "incomplete":

                summary.incomplete,

            "structural":

                summary.structural,

            "duplicate":

                summary.duplicate,

            "schema_error":

                summary.schema_error,

            "reference_required":

                summary.reference_required,

            "coverage":

                summary.coverage,

        }

    # -----------------------------------------------------

    def print_console(
        self,
        summary: ValidationSummary,
    ):

        print()

        print("=" * 60)

        print("AulaMind Curriculum Coverage Report")

        print("=" * 60)

        print()

        print(f"Documentos analizados : {summary.total}")

        print(f"VALID                : {summary.valid}")

        print(f"INCOMPLETE           : {summary.incomplete}")

        print(f"STRUCTURAL           : {summary.structural}")

        print(f"DUPLICATE            : {summary.duplicate}")

        print(f"SCHEMA_ERROR         : {summary.schema_error}")

        print(f"REFERENCE_REQUIRED   : {summary.reference_required}")

        print()

        print(f"Cobertura curricular : {summary.coverage}%")

        print()

        print("=" * 60)

    # -----------------------------------------------------

    def statistics(self):

        return {

            "module":

                "Coverage Report",

            "version":

                "Semana 5A.5",

        }


coverage_report = CoverageReport()