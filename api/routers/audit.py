"""
===========================================================
AulaMind Enterprise 3.0

Audit Router

Sprint 9.3
===========================================================
"""

from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter

from services.curriculum_auditor.auditor import (
    curriculum_auditor,
)

router = APIRouter()

# ---------------------------------------------------------
# Ruta del currículo
# ---------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[2]

CURRICULUM_PATH = PROJECT_ROOT / "data_curricular"


# ---------------------------------------------------------
# Función privada
# ---------------------------------------------------------

def _audit():

    return curriculum_auditor.audit(
        CURRICULUM_PATH
    )


# ---------------------------------------------------------
# GET /audit
# ---------------------------------------------------------

@router.get(
    "",
    summary="AuditReport completo",
)
def get_audit():

    return _audit()


# ---------------------------------------------------------
# GET /audit/summary
# ---------------------------------------------------------

@router.get(
    "/summary",
    summary="Resumen Ejecutivo",
)
def get_summary():

    report = _audit()

    return report.summary


# ---------------------------------------------------------
# GET /audit/status
# ---------------------------------------------------------

@router.get(
    "/status",
    summary="Estados",
)
def get_status():

    report = _audit()

    return report.status


# ---------------------------------------------------------
# GET /audit/statistics
# ---------------------------------------------------------

@router.get(
    "/statistics",
    summary="Estadísticas",
)
def get_statistics():

    report = _audit()

    return {

        "version": report.version,

        "generated_at": report.generated_at,

        "documents": report.summary.documents,

        "coverage": report.summary.coverage,

        "average_completeness":
            report.summary.average_completeness,

        "valid":
            report.valid_documents,

        "incomplete":
            report.incomplete_documents,

        "duplicates":
            report.duplicate_documents,

    }


# ---------------------------------------------------------
# GET /audit/modalities
# ---------------------------------------------------------

@router.get(
    "/modalities",
    summary="Modalidades",
)
def get_modalities():

    report = _audit()

    return report.modalities


# ---------------------------------------------------------
# GET /audit/courses
# ---------------------------------------------------------

@router.get(
    "/courses",
    summary="Cursos",
)
def get_courses():

    report = _audit()

    return report.courses


# ---------------------------------------------------------
# GET /audit/subjects
# ---------------------------------------------------------

@router.get(
    "/subjects",
    summary="Asignaturas",
)
def get_subjects():

    report = _audit()

    return report.subjects