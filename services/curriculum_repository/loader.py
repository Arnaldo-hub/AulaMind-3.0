"""
===========================================================
AulaMind Enterprise 3.0

Curriculum Repository

Loader

Sprint 9.6.7
===========================================================

Responsabilidad

Localizar y cargar documentos curriculares.

Este componente NO construye índices.

NO realiza búsquedas.

NO depende del Repository.

Simplemente devuelve una colección de documentos.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any
import json


class CurriculumLoader:
    """
    Cargador oficial del currículo.
    """

    def __init__(self):

        self._extensions = {
            ".json",
        }

    # ---------------------------------------------------------

    def discover(
        self,
        root: Path,
    ) -> list[Path]:
        """
        Descubre todos los documentos curriculares.
        """

        files: list[Path] = []

        if not root.exists():
            return files

        for extension in self._extensions:

            files.extend(
                root.rglob(f"*{extension}")
            )

        return sorted(files)

    # ---------------------------------------------------------

    def load_document(
        self,
        path: Path,
    ) -> Any:
        """
        Carga un documento JSON.
        """

        with path.open(
            "r",
            encoding="utf-8",
        ) as fp:

            return json.load(fp)

    # ---------------------------------------------------------

    def load(
        self,
        root: Path,
    ) -> list[Any]:
        """
        Carga todos los documentos del currículo.
        """

        documents: list[Any] = []

        for file in self.discover(root):

            try:

                document = self.load_document(
                    file
                )

                documents.append(document)

            except Exception as ex:

                print(
                    f"[Loader] Error: {file}"
                )

                print(ex)

        return documents

    # ---------------------------------------------------------

    def statistics(
        self,
        root: Path,
    ) -> dict:
        """
        Estadísticas básicas del Loader.
        """

        files = self.discover(root)

        return {

            "files": len(files),

            "extensions": sorted(
                self._extensions
            ),

            "root": str(root),

        }


curriculum_loader = CurriculumLoader()