"""
===========================================================
AulaMind Enterprise 3.0

Curriculum Repository

Versión 4

Sprint 9.6.11
===========================================================

Repository oficial del currículo.

Punto único de acceso al dominio curricular.

Toda la plataforma deberá consultar el currículo
exclusivamente mediante este componente.
"""

from __future__ import annotations

from pathlib import Path

from services.curriculum_repository.index import CurriculumIndex
from services.curriculum_repository.loader import curriculum_loader
from services.curriculum_repository.search import CurriculumSearch


class CurriculumRepository:

    def __init__(self):

        self._index = CurriculumIndex()

        self._search = CurriculumSearch(
            self._index
        )

        self._root = None

    # ---------------------------------------------------------

    def initialize(
        self,
        root: Path,
    ):

        self._root = root

        documents = curriculum_loader.load(root)

        self._index.build(documents)

    # ---------------------------------------------------------

    def reload(self):

        if self._root is None:
            return

        self.initialize(self._root)

    # ---------------------------------------------------------

    @property
    def loaded(self):

           return len(self._index.documents) > 0


# ---------------------------------------------------------

    @property
    def root(self):

          return self._root


# ---------------------------------------------------------

    def clear(self):

        self._index.clear()

    # ---------------------------------------------------------

    def clear(self):

        self._index.clear()

    # ---------------------------------------------------------

    def documents(self):

        return self._index.documents

    # ---------------------------------------------------------

    def modalities(self):

        return self._index.modalities

    # ---------------------------------------------------------

    def courses(self):

        return self._index.courses

    # ---------------------------------------------------------

    def subjects(self):

        return self._index.subjects

    # =========================================================
    # SEARCH
    # =========================================================

    def find_modality(
        self,
        modality: str,
    ):

        return self._search.modality(
            modality
        )

    # ---------------------------------------------------------

    def find_course(
        self,
        course: str,
    ):

        return self._search.course(
            course
        )

    # ---------------------------------------------------------

    def find_subject(
        self,
        subject: str,
    ):

        return self._search.subject(
            subject
        )

    # ---------------------------------------------------------

    def contains_course(
        self,
        course: str,
    ):

        return self._search.contains_course(
            course
        )

    # ---------------------------------------------------------

    def contains_subject(
        self,
        subject: str,
    ):

        return self._search.contains_subject(
            subject
        )

    # ---------------------------------------------------------

    def contains_modality(
        self,
        modality: str,
    ):

        return self._search.contains_modality(
            modality
        )

    # ---------------------------------------------------------

    def search_courses(
        self,
        text: str,
    ):

        return self._search.courses_like(
            text
        )

    # ---------------------------------------------------------

    def search_subjects(
        self,
        text: str,
    ):

        return self._search.subjects_like(
            text
        )

    # ---------------------------------------------------------

    def search_modalities(
        self,
        text: str,
    ):

        return self._search.modalities_like(
            text
        )

    # =========================================================

    def statistics(self):

        stats = self._index.statistics()

        stats["loaded"] = self.loaded

        return stats

    # ---------------------------------------------------------

    def summary(self):

        stats = self.statistics()

        return {

            "loaded": stats["loaded"],

            "documents": stats["documents"],

            "modalities": stats["modalities"],

            "courses": stats["courses"],

            "subjects": stats["subjects"],

        }


curriculum_repository = CurriculumRepository()