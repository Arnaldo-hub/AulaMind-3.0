"""
===========================================================
AulaMind Enterprise 3.0
Curriculum Engine 4.0

TP Adapter
===========================================================
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from .base import CurriculumAdapter


class TPAdapter(CurriculumAdapter):
    """
    Adaptador para Educación Media Técnico Profesional.
    """

    mode = "tp"
    priority = 80

    def can_handle(
        self,
        path: Path,
        data: dict[str, Any],
    ) -> bool:

        path_text = str(path).lower()

        modalidad = str(
            data.get("modalidad", "")
        ).lower()

        if "especialidades_tp" in path_text:
            return True

        if "tecnico-profesional" in modalidad:
            return True

        if "técnico-profesional" in modalidad:
            return True

        if data.get("especialidad"):
            return True

        if data.get("modulos"):
            return True

        return False

    # ---------------------------------------------------------

    def adapt(
        self,
        path: Path,
        data: dict[str, Any],
    ) -> list[dict]:

        modules = data.get("modulos", [])

        unidades = []

        if isinstance(modules, list):

            for i, module in enumerate(modules, start=1):

                if not isinstance(module, dict):
                    continue

                unidades.append(
                    {
                        "id": (
                            module.get("codigo")
                            or str(i)
                        ),
                        "nombre": (
                            module.get("nombre")
                            or f"Módulo {i}"
                        ),
                        "oa": (
                            module.get("oa")
                            or module.get("oa_asociados")
                            or []
                        ),
                    }
                )

        metadata = {
            "sector": data.get("sector"),
            "especialidad": data.get("especialidad"),
            "mencion": data.get("mencion"),
            "plan": data.get("plan"),
        }

        record = self.build_record(

            level="TP",

            course=data.get(
                "curso",
                "",
            ),

            subject=(
                data.get("especialidad")
                or data.get("asignatura")
                or ""
            ),

            units=unidades,

            objectives=[],

            metadata=metadata,

        )

        return [record]