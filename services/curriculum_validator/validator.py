"""
===========================================================
AulaMind Enterprise 3.0

Curriculum Validator

Validator (Orquestador)

Semana 5A.6
===========================================================
"""

from __future__ import annotations

from pathlib import Path
import json

from .completeness_analyzer import completeness_analyzer
from .metadata_enricher import metadata_enricher
from .schema_validator import schema_validator
from .duplicate_detector import duplicate_detector
from .reference_checker import reference_checker
from .coverage_report import coverage_report
from .models import (
    ValidationResult,
    ValidationSummary,
    ValidationStatus,
)


class CurriculumValidator:
    """
    Orquestador del Curriculum Validator.

    Ejecuta todos los validadores sobre un conjunto
    de documentos curriculares y genera un informe
    consolidado.

    No modifica archivos.
    """

    # -----------------------------------------------------
    # Carpetas que NO contienen currículo
    # -----------------------------------------------------

    EXCLUDED_DIRECTORIES = {
        "__pycache__",
        "auditoria_curricular_global",
        "reportes",
        "reports",
        "logs",
        "backup",
        ".git",
        ".idea",
        ".vscode",
    }

    # -----------------------------------------------------
    # Archivos que NO deben validarse
    # -----------------------------------------------------

    EXCLUDED_PREFIXES = (
        "AUDITORIA_",
        "REPORTE_",
        "REPORT_",
        "INVENTARIO_",
        "VALIDACION_",
        "RESUMEN_",
    )
    # -----------------------------------------------------

    def __init__(self):

        self.schema = schema_validator

        self.duplicates = duplicate_detector

        self.references = reference_checker

        self.report = coverage_report

        

    # -----------------------------------------------------

    def validate_file(
        self,
        path: str | Path,
    ) -> ValidationResult:

        path = Path(path)

        try:

            with open(path, "r", encoding="utf-8") as fp:

                data = json.load(fp)

            data = metadata_enricher.enrich(path, data)

            completeness = completeness_analyzer.analyze(data)

        except Exception as ex:

            result = ValidationResult(path=str(path))

            result.set_status(
                ValidationStatus.STRUCTURAL
            )

            result.add_error(

                "JSON_LOAD",

                str(ex),

            )

            return result

        return self.validate_document(

            str(path),

            data,

        )

    # -----------------------------------------------------

    def validate_document(
        self,
        path: str,
        data: dict,
    ) -> ValidationResult:

        schema_result = self.schema.validate(

            path,

            data,

        )

        data = metadata_enricher.enrich(path, data)

        completeness = completeness_analyzer.analyze(data)

        duplicate_result = self.duplicates.validate(

            path,

            data,

        )

        reference_result = self.references.validate(

            path,

            data,

        )

        merged = self._merge(
            schema_result,
            duplicate_result,
            reference_result,
        )

        merged.metadata["completeness"] = completeness

        return merged

       
    # -----------------------------------------------------

    def _should_validate(self, file: Path) -> bool:

        file_str = str(file).lower().replace("\\", "/")

        excluded_dirs = (
            "/auditoria_curricular_global/",
            "/reportes/",
            "/reports/",
            "/logs/",
            "/backup/",
            "/__pycache__/",
            "/.git/",
            "/.idea/",
            "/.vscode/",
        )

        for folder in excluded_dirs:
            if folder in file_str:
                return False

        filename = file.name.upper()

        excluded_prefixes = (
            "AUDITORIA_",
            "REPORTE_",
            "REPORT_",
            "INVENTARIO_",
            "VALIDACION_",
            "RESUMEN_",
        )

        for prefix in excluded_prefixes:
            if filename.startswith(prefix):
                return False

        return True
    # -----------------------------------------------------

    def validate_directory(
        self,
        root: str | Path,
    ) -> ValidationSummary:

        root = Path(root)

        self.duplicates.reset()

        results = []

        for file in root.rglob("*.json"):

            if not self._should_validate(file):
                continue

            results.append(
                self.validate_file(file)
            )

        return self.report.generate(results)
    # -----------------------------------------------------

    def _merge(
        self,
        schema_result,
        duplicate_result,
        reference_result,
    ):

        result = ValidationResult(

            path=schema_result.path,

            modalidad=schema_result.modalidad,

            curso=schema_result.curso,

            asignatura=schema_result.asignatura,

        )

        priority = [

            ValidationStatus.STRUCTURAL,

            ValidationStatus.SCHEMA_ERROR,

            ValidationStatus.DUPLICATE,

            ValidationStatus.REFERENCE_REQUIRED,

            ValidationStatus.INCOMPLETE,

            ValidationStatus.VALID,

        ]

        candidates = [

            schema_result,

            duplicate_result,

            reference_result,

        ]

        status = ValidationStatus.VALID

        for candidate in candidates:

            if priority.index(candidate.estado) < priority.index(status):

                status = candidate.estado

            result.errores.extend(candidate.errores)

            result.advertencias.extend(candidate.advertencias)

            result.metadata.update(candidate.metadata)

        result.set_status(status)

        return result

    # -----------------------------------------------------

    def statistics(self):

        return {

            "validator":

                "Curriculum Validator",

            "version":

                "Semana 5A.6",

            "modules": {

                "schema": True,

                "duplicates": True,

                "references": True,

                "coverage": True,

            }

        }


curriculum_validator = CurriculumValidator()