"""
===========================================================
AulaMind Enterprise 3.0

Dashboard Service

Semana 8.4

Consume AuditReport
Produce DashboardReport
===========================================================
"""

from __future__ import annotations

from services.curriculum_auditor.models import AuditReport

from .models import (
    DashboardAlert,
    DashboardChart,
    DashboardKPI,
    DashboardRanking,
    DashboardReport,
)


class DashboardService:
    """
    Servicio de aplicación encargado de transformar
    AuditReport en DashboardReport.

    No realiza cálculos curriculares.
    No valida documentos.
    No recorre JSON.

    Es la capa de adaptación entre el Auditor
    y el Dashboard Web.
    """

    VERSION = "8.4"

    # -----------------------------------------------------

    def build(
        self,
        report: AuditReport,
    ) -> DashboardReport:

        kpis = DashboardKPI(

            documents=report.summary.documents,

            coverage=report.summary.coverage,

            average_completeness=report.summary.average_completeness,

            valid=report.valid_documents,

            incomplete=report.incomplete_documents,

            duplicates=report.duplicate_documents,

        )

        dashboard = DashboardReport(

            version=self.VERSION,

            generated_at=report.generated_at,

            kpis=kpis,

            executive_summary=report.executive_summary,

            alerts=self._build_alerts(report),

            modalities=report.modalities,

            courses=report.courses,

            subjects=report.subjects,

            top_valid=report.top_valid,

            top_incomplete=report.top_incomplete,

            duplicates=report.duplicates,

            charts=self._build_charts(report),

            rankings=self._build_rankings(report),

        )

        return dashboard

    # -----------------------------------------------------

    def get_kpis(
        self,
        report: AuditReport,
    ) -> DashboardKPI:
        """
        Devuelve únicamente los KPIs del Dashboard.
        """

        return self.build(report).kpis

    # -----------------------------------------------------

    def get_alerts(
        self,
        report: AuditReport,
    ) -> list[DashboardAlert]:
        """
        Devuelve las alertas del Dashboard.
        """

        return self.build(report).alerts

    # -----------------------------------------------------

    def get_charts(
        self,
        report: AuditReport,
    ) -> list[DashboardChart]:
        """
        Devuelve los gráficos del Dashboard.
        """

        return self.build(report).charts

    # -----------------------------------------------------

    def get_rankings(
        self,
        report: AuditReport,
    ) -> list[DashboardRanking]:
        """
        Devuelve los rankings del Dashboard.
        """

        return self.build(report).rankings

    # -----------------------------------------------------

    def _build_alerts(
        self,
        report: AuditReport,
    ) -> list[DashboardAlert]:

        alerts: list[DashboardAlert] = []

        if report.duplicate_documents:

            alerts.append(

                DashboardAlert(

                    level="warning",

                    title="Documentos duplicados",

                    message=(
                        f"Se detectaron "
                        f"{report.duplicate_documents} "
                        f"documentos duplicados."
                    ),

                )

            )

        if report.incomplete_documents:

            alerts.append(

                DashboardAlert(

                    level="info",

                    title="Currículo incompleto",

                    message=(
                        f"Existen "
                        f"{report.incomplete_documents} "
                        f"documentos incompletos."
                    ),

                )

            )

        if report.summary.coverage < 80:

            alerts.append(

                DashboardAlert(

                    level="critical",

                    title="Cobertura curricular baja",

                    message=(
                        f"La cobertura actual es "
                        f"{report.summary.coverage}%"
                    ),

                )

            )

        return alerts

    # -----------------------------------------------------

    def _build_charts(
        self,
        report: AuditReport,
    ) -> list[DashboardChart]:

        return [

            DashboardChart(

                title="Estados",

                labels=list(report.status.keys()),

                values=list(report.status.values()),

            ),

            DashboardChart(

                title="Modalidades",

                labels=[name for name, _ in report.modalities],

                values=[value for _, value in report.modalities],

            ),

        ]

    # -----------------------------------------------------

    def _build_rankings(
        self,
        report: AuditReport,
    ) -> list[DashboardRanking]:

        return [

            DashboardRanking(

                title="Documentos más completos",

                items=report.top_valid,

            ),

            DashboardRanking(

                title="Documentos incompletos",

                items=report.top_incomplete,

            ),

        ]

    # -----------------------------------------------------

    def statistics(self):

        return {

            "module": "Dashboard Service",

            "version": self.VERSION,

            "input": "AuditReport",

            "output": "DashboardReport",

        }


dashboard_service = DashboardService()