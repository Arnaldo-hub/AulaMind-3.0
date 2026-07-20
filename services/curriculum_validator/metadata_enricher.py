"""
===========================================================
AulaMind Enterprise 3.0

Curriculum Validator

Metadata Enricher

Semana 5B.1
===========================================================
"""

from __future__ import annotations

from pathlib import Path
from typing import Any


class MetadataEnricher:
    """
    Completa automáticamente metadatos curriculares
    que pueden inferirse desde la ruta del archivo
    o desde la estructura del JSON.
    """

    def enrich(
        self,
        path: str | Path,
        data: dict[str, Any],
    ) -> dict[str, Any]:

        if not isinstance(data, dict):
            return data

        path = Path(path)

        data.setdefault("fuente", "Currículum Nacional MINEDUC")

        data.setdefault("estado_curricular", "vigente")

        if "marco" not in data:

            data["marco"] = self._infer_marco(path)

        if not data.get("nivel"):

            nivel = self._infer_nivel(path)

            if nivel:

                data["nivel"] = nivel

        if not data.get("modalidad"):

            modalidad = self._infer_modalidad(path)

            if modalidad:

                data["modalidad"] = modalidad

        return data

    # ---------------------------------------------------------

    def _infer_modalidad(
        self,
        path: Path,
    ) -> str:

        p = str(path).lower()

        if "parvularia" in p:
            return "parvularia"

        if "epja" in p:
            return "epja"

        if "especialidades_tp" in p:
            return "tp"

        if "electivos_profundizacion_hc" in p:
            return "hc"

        return "regular"

    # ---------------------------------------------------------

    def _infer_marco(
        self,
        path: Path,
    ) -> str:

        modalidad = self._infer_modalidad(path)

        mapping = {

            "regular":
                "Bases Curriculares",

            "hc":
                "Formación General Electiva",

            "tp":
                "Formación Diferenciada Técnico Profesional",

            "parvularia":
                "Bases Curriculares Educación Parvularia",

            "epja":
                "Marco EPJA",

        }

        return mapping.get(
            modalidad,
            "Currículum Nacional",
        )

    # ---------------------------------------------------------

    def _infer_nivel(
        self,
        path: Path,
    ) -> str | None:

        text = str(path).lower()

        cursos = [

            "1_basico",
            "2_basico",
            "3_basico",
            "4_basico",
            "5_basico",
            "6_basico",
            "7_basico",
            "8_basico",
            "1_medio",
            "2_medio",
            "3_medio",
            "4_medio",

        ]

        for curso in cursos:

            if curso in text:

                return curso.replace(
                    "_",
                    " "
                )

        return None

    # ---------------------------------------------------------

    def statistics(self):

        return {

            "module":
                "Metadata Enricher",

            "version":
                "5B.1",

            "automatic_fields": [

                "fuente",

                "marco",

                "estado_curricular",

                "nivel",

                "modalidad",

            ]

        }


metadata_enricher = MetadataEnricher()