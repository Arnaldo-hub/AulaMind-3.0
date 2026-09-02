"""
===========================================================
AulaMind Enterprise 3.0
services/jobs/fonoaudiologia_job.py
-----------------------------------------------------------
Tarea en background para generación fonoaudiológica
===========================================================
"""

from services.fonoaudiologia_service import FonoaudiologiaService
from services.persistence_service import persistence_service
from services.entitlements import Entitlements

fono_service = FonoaudiologiaService()


def generate_fonoaudiologia_job(user_id: str, school_id: str | None, payload: dict, tipo: str):
    """
    Ejecutada por el worker RQ (si existe) o síncronamente.
    Genera documento fonoaudiológico y persiste en BD.
    """
    if tipo == "informe":
        result = fono_service.generar_informe(payload)
        doc_type = "fonoaudiologia_informe"
    elif tipo == "plan":
        result = fono_service.generar_plan_intervencion(payload)
        doc_type = "fonoaudiologia_plan"
    elif tipo == "consejos":
        result = fono_service.generar_consejos_docente(payload)
        doc_type = "fonoaudiologia_consejos"
    else:
        return {"success": False, "error": "Tipo desconocido"}

    if not result.get("success"):
        return result

    # Registrar consumo de generación
    Entitlements.record_generation(user_id)

    # Guardar documento
    document_id = persistence_service.save_generated_document(
        user_id=user_id,
        school_id=school_id,
        document_type=doc_type,
        payload=payload,
        result=result,
    )

    return {
        "success": True,
        "document_id": document_id,
        "content": result.get("content"),
    }