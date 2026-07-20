"""
===========================================================
AulaMind Enterprise 3.0

Planning Router

Sprint 9.5
===========================================================
"""

from __future__ import annotations

from fastapi import APIRouter

from services.planning_service import planning_service

router = APIRouter()


# ---------------------------------------------------------
# POST /planning
# ---------------------------------------------------------

@router.post(
    "",
    summary="Generar planificación",
)
def generate_planning(
    data: dict,
):

    return planning_service.generate(
        data
    )


# ---------------------------------------------------------
# POST /planning/preview
# ---------------------------------------------------------

@router.post(
    "/preview",
    summary="Vista previa",
)
def preview_planning(
    data: dict,
):

    return planning_service.preview(
        data
    )


# ---------------------------------------------------------
# POST /planning/validate
# ---------------------------------------------------------

@router.post(
    "/validate",
    summary="Validar solicitud",
)
def validate_planning(
    data: dict,
):

    valid, message = planning_service.validate(
        data
    )

    return {

        "valid": valid,

        "message": message,

    }


# ---------------------------------------------------------
# GET /planning/sample
# ---------------------------------------------------------

@router.get(
    "/sample",
    summary="Ejemplo",
)
def sample():

    return planning_service.sample()


# ---------------------------------------------------------
# GET /planning/empty
# ---------------------------------------------------------

@router.get(
    "/empty",
    summary="Plantilla vacía",
)
def empty():

    return planning_service.empty()


# ---------------------------------------------------------
# GET /planning/status
# ---------------------------------------------------------

@router.get(
    "/status",
    summary="Estado del servicio",
)
def status():

    return planning_service.health()