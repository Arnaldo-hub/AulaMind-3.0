from pathlib import Path
from typing import Any

from .base import CurriculumAdapter


class HCAdapter(CurriculumAdapter):

    mode = "hc"
    priority = 20

    def can_handle(
        self,
        path: Path,
        data: dict[str, Any],
    ) -> bool:

        modalidad = str(
            data.get(
                "modalidad",
                "",
            )
        ).lower()

        return (

            "hc" in modalidad

            or "human" in modalidad

            or "electivos_profundizacion_hc"
            in str(path).lower()

        )

    def adapt(
        self,
        path: Path,
        data: dict[str, Any],
    ) -> list[dict]:

        return [

            self.build_record(

                level=data.get(
                    "nivel",
                    "3° medio HC",
                ),

                course=data.get(
                    "curso",
                    "",
                ),

                subject=data.get(
                    "asignatura",
                    "",
                ),

                units=self.unit_records(
                    data.get("unidades")
                ),

                objectives=data.get(
                    "oa",
                    [],
                ),

                metadata={},
            )

        ]