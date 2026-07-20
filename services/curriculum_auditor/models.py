"""
===========================================================
AulaMind Enterprise 3.0

Curriculum Auditor

Domain Models

Semana 7.1
===========================================================
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


# ---------------------------------------------------------
# Resumen General
# ---------------------------------------------------------

@dataclass(slots=True)
class AuditSummary:

    documents: int = 0

    coverage: float = 0.0

    average_completeness: float = 0.0


# ---------------------------------------------------------
# Elemento de Ranking
# ---------------------------------------------------------

@dataclass(slots=True)
class RankingItem:

    path: str = ""

    modalidad: str = ""

    curso: str = ""

    asignatura: str = ""

    score: float = 0.0

    estado: str = ""


# ---------------------------------------------------------
# Reporte Oficial del Auditor
# ---------------------------------------------------------

@dataclass(slots=True)
class AuditReport:

    version: str

    generated_at: str

    summary: AuditSummary

    status: dict[str, int] = field(default_factory=dict)

    modalities: list[tuple[str, int]] = field(default_factory=list)

    courses: list[tuple[str, int]] = field(default_factory=list)

    subjects: list[tuple[str, int]] = field(default_factory=list)

    top_valid: list[dict[str, Any]] = field(default_factory=list)

    top_incomplete: list[dict[str, Any]] = field(default_factory=list)

    duplicates: list[dict[str, Any]] = field(default_factory=list)

    executive_summary: str = ""

    # -----------------------------------------------------

    @property
    def valid_documents(self) -> int:

        return self.status.get("VALID", 0)

    # -----------------------------------------------------

    @property
    def incomplete_documents(self) -> int:

        return self.status.get("INCOMPLETE", 0)

    # -----------------------------------------------------

    @property
    def duplicate_documents(self) -> int:

        return self.status.get("DUPLICATE", 0)

    # -----------------------------------------------------

    @property
    def completion_ratio(self) -> float:

        return self.summary.average_completeness

    # -----------------------------------------------------

    def statistics(self):

        return {

            "model": "AuditReport",

            "version": self.version,

            "documents": self.summary.documents,

            "coverage": self.summary.coverage,

        }