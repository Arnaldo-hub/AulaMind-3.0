"""
===========================================================
AulaMind Enterprise 3.0
Curriculum Engine 4.0

Parvularia Adapter
===========================================================
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from .base import CurriculumAdapter


class ParvulariaAdapter(CurriculumAdapter):
    """
    Adaptador para Educación Parvularia.
    """

    mode = "parvularia"
    priority = 70

    # ---------------------------------------------------------

    def can_handle(
        self,
        path: Path,
        data: dict[str, Any],
    ) -> bool:

        path_text = str(path).lower()

        if "educacion_parvularia" in path_text:
            return True

        nivel = str(
            data.get("nivel", "")
        ).lower()

        if nivel.startswith("nt1"):
            return True

        if nivel.startswith("nt2"):
            return True

        if data.get("ambito"):
            return True

        if data.get("nucleos"):
            return True

        return False

    # ---------------------------------------------------------

    def adapt(
        self,
        path: Path,
        data: dict[str, Any],
    ) -> list[dict]:

        unidades = []

        nucleos = data.get("nucleos", [])

        if isinstance(nucleos, list):

            for index, nucleo in enumerate(nucleos, start=1):

                if not isinstance(nucleo, dict):
                    continue

                unidades.append(
                    {
                        "id": (
                            nucleo.get("codigo")
                            or str(index)
                        ),

                        "nombre": (
                            nucleo.get("nombre")
                            or f"Núcleo {index}"
                        ),

                        "oa": (
                            nucleo.get("oa")
                            or nucleo.get("objetivos")
                            or []
                        ),
                    }
                )

        metadata = {

            "ambito": data.get("ambito"),

            "nivel": data.get("nivel"),

        }

        record = self.build_record(

            level="Parvularia",

            course=data.get(
                "nivel",
                "",
            ),

            subject=data.get(
                "ambito",
                "",
            ),

            units=unidades,

            objectives=[],

            metadata=metadata,

        )

        return [record]