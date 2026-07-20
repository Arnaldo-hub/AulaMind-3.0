"""
===========================================================
AulaMind Enterprise 3.0

Dashboard

Domain Models

Semana 8.3
===========================================================
"""

from __future__ import annotations

from dataclasses import dataclass, field


# ---------------------------------------------------------
# KPI PRINCIPALES
# ---------------------------------------------------------

@dataclass(slots=True)
class DashboardKPI:

    documents: int = 0

    coverage: float = 0.0

    average_completeness: float = 0.0

    valid: int = 0

    incomplete: int = 0

    duplicates: int = 0


# ---------------------------------------------------------
# ALERTAS
# ---------------------------------------------------------

@dataclass(slots=True)
class DashboardAlert:

    level: str

    title: str

    message: str


# ---------------------------------------------------------
# ELEMENTO DE RANKING
# ---------------------------------------------------------

@dataclass(slots=True)
class DashboardRanking:

    title: str

    items: list = field(default_factory=list)


# ---------------------------------------------------------
# DATOS PARA GRÁFICOS
# ---------------------------------------------------------

@dataclass(slots=True)
class DashboardChart:

    title: str

    labels: list[str] = field(default_factory=list)

    values: list[float] = field(default_factory=list)


# ---------------------------------------------------------
# MODELO OFICIAL DEL DASHBOARD
# ---------------------------------------------------------

@dataclass(slots=True)
class DashboardReport:

    version: str

    generated_at: str

    kpis: DashboardKPI

    executive_summary: str

    alerts: list[DashboardAlert] = field(default_factory=list)

    modalities: list[tuple[str, int]] = field(default_factory=list)

    courses: list[tuple[str, int]] = field(default_factory=list)

    subjects: list[tuple[str, int]] = field(default_factory=list)

    top_valid: list[dict] = field(default_factory=list)

    top_incomplete: list[dict] = field(default_factory=list)

    duplicates: list[dict] = field(default_factory=list)

    charts: list[DashboardChart] = field(default_factory=list)

    rankings: list[DashboardRanking] = field(default_factory=list)

    # -----------------------------------------------------

    @property
    def total_alerts(self) -> int:

        return len(self.alerts)

    # -----------------------------------------------------

    @property
    def has_critical_alerts(self) -> bool:

        return any(
            alert.level.lower() == "critical"
            for alert in self.alerts
        )

    # -----------------------------------------------------

    @property
    def healthy(self) -> bool:

        return (
            self.kpis.coverage >= 90
            and self.kpis.duplicates == 0
            and self.kpis.incomplete == 0
        )

    # -----------------------------------------------------

    def statistics(self):

        return {

            "model": "DashboardReport",

            "version": self.version,

            "documents": self.kpis.documents,

            "coverage": self.kpis.coverage,

            "alerts": self.total_alerts,

        }