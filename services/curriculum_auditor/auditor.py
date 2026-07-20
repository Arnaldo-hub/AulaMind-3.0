"""
===========================================================
AulaMind Enterprise 3.0

Curriculum Auditor

Orquestador

Semana 7.3
===========================================================
"""

from __future__ import annotations

from pathlib import Path

from services.curriculum_validator.validator import curriculum_validator

from .statistics import statistics_engine
from .ranking import ranking_engine
from .executive_report import executive_report
from .models import AuditReport


class CurriculumAuditor:
    """
    Orquestador principal del Curriculum Auditor.

    Flujo:

        Curriculum Validator
                │
                ▼
        Statistics Engine
                │
                ▼
        Ranking Engine
                │
                ▼
        Executive Report
                │
                ▼
            AuditReport
    """

    VERSION = "7.3"

    # ---------------------------------------------------------

    def audit(
        self,
        curriculum_root: str | Path,
    ) -> AuditReport:

        curriculum_root = Path(curriculum_root)

        validation = curriculum_validator.validate_directory(
            curriculum_root
        )

        statistics = statistics_engine.calculate(
            validation.results
        )

        rankings = ranking_engine.build(
            statistics
        )

        statistics.update(rankings)

        report = executive_report.generate(
            statistics
        )

        return report

    # ---------------------------------------------------------

    def statistics(self):

        return {

            "module": "Curriculum Auditor",

            "version": self.VERSION,

            "returns": "AuditReport",

            "pipeline": [

                "Curriculum Validator",

                "Statistics Engine",

                "Ranking Engine",

                "Executive Report",

            ],

        }


curriculum_auditor = CurriculumAuditor()