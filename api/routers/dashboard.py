"""
===========================================================
AulaMind Enterprise 3.0

Dashboard Router

Sprint 9.2
===========================================================
"""

from __future__ import annotations

from fastapi import APIRouter

from api.providers.dashboard_provider import (
    dashboard_provider,
)

router = APIRouter()

# ---------------------------------------------------------
# GET /dashboard
# ---------------------------------------------------------

@router.get(
    "",
    summary="Dashboard completo",
)
def get_dashboard():

    return dashboard_provider.build()


# ---------------------------------------------------------
# GET /dashboard/kpis
# ---------------------------------------------------------

@router.get(
    "/kpis",
    summary="KPIs principales",
)
def get_kpis():

    return dashboard_provider.kpis()


# ---------------------------------------------------------
# GET /dashboard/alerts
# ---------------------------------------------------------

@router.get(
    "/alerts",
    summary="Alertas",
)
def get_alerts():

    return dashboard_provider.alerts()


# ---------------------------------------------------------
# GET /dashboard/rankings
# ---------------------------------------------------------

@router.get(
    "/rankings",
    summary="Rankings",
)
def get_rankings():

    return dashboard_provider.rankings()

# ---------------------------------------------------------
# GET /dashboard/charts
# ---------------------------------------------------------

@router.get(
    "/charts",
    summary="Gráficos",
)
def get_charts():

    return dashboard_provider.charts()

# ---------------------------------------------------------
# GET /dashboard/modalities
# ---------------------------------------------------------
@router.get(
    "/modalities",
    summary="Modalidades",
)
def get_modalities():

    return dashboard_provider.build().modalities

# ---------------------------------------------------------
# GET /dashboard/modalities
# ---------------------------------------------------------

@router.get(
    "/modalities",
    summary="Modalidades",
)
def get_modalities():

    return dashboard_provider.build().modalities

# ---------------------------------------------------------
# GET /dashboard/courses
# ---------------------------------------------------------

@router.get(
    "/courses",
    summary="Cursos",
)
def get_courses():

    return dashboard_provider.build().courses

# ---------------------------------------------------------
# GET /dashboard/subjects
# ---------------------------------------------------------

@router.get(
    "/subjects",
    summary="Asignaturas",
)
def get_subjects():

    return dashboard_provider.build().subjects