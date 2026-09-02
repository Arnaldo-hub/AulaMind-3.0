"""
===========================================================
AulaMind Enterprise 3.0
services/jobs/pie_job.py
-----------------------------------------------------------
Tarea en background: generar PIE y persistir resultado
===========================================================
"""

from services.pie_service import PIEService
from services.persistence_service import persistence_service
from services.entitlements import Entitlements


def generate_pie_job(user_id: str, school_id: str | None, payload: dict):
    """
    Ejecutada por el worker RQ. No tiene acceso a Flask request context,
    por eso recibe datos primitivos y usa SessionLocal directamente.
    """
    pie_service = PIEService()
    result = pie_service.generate(payload)

    if not result.get("success"):
        return {
            "success": False,
            "error": result.get("error", "Error en generación IA"),
        }

    # Registrar consumo de generación (trial o plan pagado)
    Entitlements.record_generation(user_id)

    # Guardar documento en BD
    document_id = persistence_service.save_generated_document(
        user_id=user_id,
        school_id=school_id,
        document_type="pie",
        payload=payload,
        result=result,
    )

    return {
        "success": True,
        "document_id": document_id,
        "content": result.get("content"),
    }