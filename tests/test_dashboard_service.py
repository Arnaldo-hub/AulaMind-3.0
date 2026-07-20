"""
===========================================================
AulaMind Enterprise 3.0

Dashboard Service Test

Semana 8.5
===========================================================
"""

from pathlib import Path

from services.curriculum_auditor.auditor import (
    curriculum_auditor,
)

from services.dashboard.dashboard_service import (
    dashboard_service,
)


def main():

    root = Path(__file__).resolve().parents[1]

    curriculum = root / "data_curricular"

    print()
    print("=" * 60)
    print("AulaMind Dashboard Service")
    print("=" * 60)
    print()

    # -----------------------------------------------------
    # AuditReport
    # -----------------------------------------------------

    report = curriculum_auditor.audit(curriculum)

    # -----------------------------------------------------
    # DashboardReport
    # -----------------------------------------------------

    dashboard = dashboard_service.build(report)

    # -----------------------------------------------------
    # Validaciones del contrato
    # -----------------------------------------------------

    assert dashboard.kpis.documents > 0

    assert dashboard.kpis.coverage >= 0

    assert dashboard.kpis.average_completeness >= 0

    assert dashboard.kpis.valid >= 0

    assert dashboard.kpis.incomplete >= 0

    assert dashboard.kpis.duplicates >= 0

    assert isinstance(
        dashboard.executive_summary,
        str,
    )

    assert len(dashboard.alerts) > 0

    assert len(dashboard.charts) > 0

    assert len(dashboard.rankings) > 0

    # -----------------------------------------------------

    print("KPIs")
    print("-----")

    print(
        f"Documentos : {dashboard.kpis.documents}"
    )

    print(
        f"Cobertura  : {dashboard.kpis.coverage}%"
    )

    print(
        f"Completitud: "
        f"{dashboard.kpis.average_completeness}%"
    )

    print(
        f"Válidos    : {dashboard.kpis.valid}"
    )

    print(
        f"Incompletos: {dashboard.kpis.incomplete}"
    )

    print(
        f"Duplicados : {dashboard.kpis.duplicates}"
    )

    print()

    print("Alertas")
    print("--------")

    for alert in dashboard.alerts:

        print(
            f"[{alert.level.upper()}] {alert.title}"
        )

        print(
            f"  {alert.message}"
        )

    print()

    print("Resumen Ejecutivo")
    print("-----------------")

    print(
        dashboard.executive_summary
    )

    print()

    print("Charts")
    print("------")

    for chart in dashboard.charts:

        print(
            f"{chart.title}: "
            f"{len(chart.labels)} elementos"
        )

    print()

    print("Rankings")
    print("--------")

    for ranking in dashboard.rankings:

        print(
            f"{ranking.title}: "
            f"{len(ranking.items)} registros"
        )

    print()

    print("=" * 60)
    print("DASHBOARD REPORT OK")
    print("=" * 60)


if __name__ == "__main__":

    main()