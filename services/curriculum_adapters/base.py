from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any


class CurriculumAdapter(ABC):
    """
    Clase base para todos los adaptadores curriculares.
    """

    mode = "base"
    priority = 0

    @abstractmethod
    def can_handle(
        self,
        path: Path,
        data: dict[str, Any],
    ) -> bool:
        pass

    @abstractmethod
    def adapt(
        self,
        path: Path,
        data: dict[str, Any],
    ) -> list[dict]:
        pass

    # ---------------------------------------------------------

    def unit_records(self, units):

        if not isinstance(units, list):
            return []

        result = []

        for index, unit in enumerate(units, start=1):

            if not isinstance(unit, dict):
                continue

            oa = unit.get("oa") or unit.get("objetivos") or []

            if not isinstance(oa, list):
                oa = []

            result.append(
                {
                    "id": str(unit.get("id") or unit.get("codigo") or index),
                    "nombre": unit.get("nombre")
                    or unit.get("titulo")
                    or f"Unidad {index}",
                    "oa": oa,
                }
            )

        return result

    # ---------------------------------------------------------

    def build_record(
        self,
        *,
        level: str,
        course: str,
        subject: str,
        units: list,
        objectives: list | None = None,
        metadata: dict | None = None,
    ) -> dict:

        return {
            "modalidad": self.mode,
            "nivel": str(level or ""),
            "curso": str(course or "").strip(),
            "asignatura": str(subject or "").strip(),
            "unidades": units if isinstance(units, list) else [],
            "oa_generales": objectives if isinstance(objectives, list) else [],
            "metadata": metadata if isinstance(metadata, dict) else {},
        }