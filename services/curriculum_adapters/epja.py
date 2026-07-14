"""
===========================================================
AulaMind Enterprise 3.0
Curriculum Engine 4.0

EPJA Adapter
===========================================================
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from .base import CurriculumAdapter


class EPJAAdapter(CurriculumAdapter):
    """
    Adaptador para Educación de Personas Jóvenes y Adultas.
    """

    mode = "epja"
    priority = 75

    # ---------------------------------------------------------

    def can_handle(
        self,
        path: Path,
        data: dict[str, Any],
    ) -> bool:

        path_text = str(path).lower()

        if "epja" in path_text:
            return True

        modalidad = str(
            data.get("modalidad", "")
        ).lower()

        if modalidad == "epja":
            return True

        if "educación de personas jóvenes y adultas" in modalidad:
            return True

        if "educacion de personas jovenes y adultas" in modalidad:
            return True

        if data.get("tramo"):
            return True

        return False

    # ---------------------------------------------------------

    def adapt(
        self,
        path: Path,
        data: dict[str, Any],
    ) -> list[dict]:

        unidades = self.unit_records(
            data.get("unidades")
        )

        metadata = {

            "tramo": data.get("tramo"),

            "nivel": data.get("nivel"),

            "modalidad": data.get("modalidad"),

        }

        objectives = (

            data.get("oa")

            or data.get("objetivos")

            or []

        )

        if not isinstance(objectives, list):

            objectives = []

        record = self.build_record(

            level="EPJA",

            course=(

                data.get("nivel")

                or data.get("curso")

                or ""

            ),

            subject=data.get(

                "asignatura",

                "",

            ),

            units=unidades,

            objectives=objectives,

            metadata=metadata,

        )

        return [record]