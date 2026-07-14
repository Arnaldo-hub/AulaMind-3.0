from pathlib import Path
from typing import Any

from .base import CurriculumAdapter


class RegularAdapter(CurriculumAdapter):

    mode = "regular"
    priority = 10

    def can_handle(
        self,
        path: Path,
        data: dict[str, Any],
    ) -> bool:

        return bool(data.get("curso")) and bool(
            data.get("asignatura")
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
                    "Educación Regular",
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