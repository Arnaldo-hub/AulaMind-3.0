"""
===========================================================
AulaMind Enterprise 3.0

Dashboard Provider

Sprint 9.4A
===========================================================

Este módulo encapsula la obtención del DashboardReport
para la API REST.

Los routers no conocen cómo se construye el Dashboard.
Simplemente consumen este provider.
"""

from __future__ import annotations

from pathlib import Path

from services.curriculum_auditor.auditor import (
    curriculum_auditor,
)

from services.dashboard.dashboard_service import (
    dashboard_service,
)

PROJECT_ROOT = Path(__file__).resolve().parents[2]

CURRICULUM_PATH = PROJECT_ROOT / "data_curricular"


class DashboardProvider:
    """
    Provider de Dashboard para la API.
    """

    def build(self):
        """
        Devuelve el Dashboard completo.
        """

        report = curriculum_auditor.audit(
            CURRICULUM_PATH
        )

        return dashboard_service.build(
            report
        )

    def kpis(self):
        """
        Devuelve únicamente los KPIs.
        """

        report = curriculum_auditor.audit(
            CURRICULUM_PATH
        )

        return dashboard_service.get_kpis(
            report
        )

    def alerts(self):
        """
        Devuelve únicamente las alertas.
        """

        report = curriculum_auditor.audit(
            CURRICULUM_PATH
        )

        return dashboard_service.get_alerts(
            report
        )

    def charts(self):
        """
        Devuelve los gráficos.
        """

        report = curriculum_auditor.audit(
            CURRICULUM_PATH
        )

        return dashboard_service.get_charts(
            report
        )

    def rankings(self):
        """
        Devuelve los rankings.
        """

        report = curriculum_auditor.audit(
            CURRICULUM_PATH
        )

        return dashboard_service.get_rankings(
            report
        )


dashboard_provider = DashboardProvider()