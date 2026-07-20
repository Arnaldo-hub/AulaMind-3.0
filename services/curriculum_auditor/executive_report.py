"""
===========================================================
AulaMind Enterprise 3.0

Curriculum Auditor

Executive Report

Semana 7.2
===========================================================
"""

from __future__ import annotations

from datetime import datetime

from .models import (
    AuditReport,
    AuditSummary,
)


class ExecutiveReport:

    """
    Construye el modelo oficial AuditReport.

    Este módulo NO calcula estadísticas.
    Solo transforma el resultado del Auditor
    en un modelo estable.
    """

    VERSION = "7.2"

    # ---------------------------------------------------------

    def generate(
        self,
        audit: dict,
    ) -> AuditReport:

        summary = AuditSummary(

            documents=audit.get(
                "documents",
                0,
            ),

            coverage=audit.get(
                "coverage",
                0,
            ),

            average_completeness=audit.get(
                "average_completeness",
                0,
            ),

        )

        report = AuditReport(

            version=self.VERSION,

            generated_at=datetime.now().isoformat(),

            summary=summary,

            status=audit.get(
                "status",
                {},
            ),

            modalities=audit.get(
                "modalities",
                [],
            ),

            courses=audit.get(
                "courses",
                [],
            ),

            subjects=audit.get(
                "subjects",
                [],
            ),

            top_valid=audit.get(
                "top_valid",
                [],
            ),

            top_incomplete=audit.get(
                "top_incomplete",
                [],
            ),

            duplicates=audit.get(
                "duplicates",
                [],
            ),

            executive_summary="",

        )

        report.executive_summary = self._build_summary(
            report
        )

        return report

    # ---------------------------------------------------------

    def _build_summary(
        self,
        report: AuditReport,
    ) -> str:

        return (

            f"Se analizaron "

            f"{report.summary.documents} documentos. "

            f"La cobertura curricular es "

            f"{report.summary.coverage}%. "

            f"La completitud promedio alcanza "

            f"{report.summary.average_completeness}%. "

            f"Documentos válidos: "

            f"{report.valid_documents}. "

            f"Incompletos: "

            f"{report.incomplete_documents}. "

            f"Duplicados: "

            f"{report.duplicate_documents}."

        )

    # ---------------------------------------------------------

    def statistics(self):

        return {

            "module": "Executive Report",

            "version": self.VERSION,

            "returns": "AuditReport",

        }


executive_report = ExecutiveReport()