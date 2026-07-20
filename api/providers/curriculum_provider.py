"""
===========================================================
AulaMind Enterprise 3.0

Curriculum Provider

Sprint 9.6.9

Versión 2
===========================================================

Provider oficial de la Curriculum API.

Responsabilidades

- Inicializar el Repository.
- Exponer información curricular.
- No conocer la implementación interna del currículo.
"""

from __future__ import annotations

from pathlib import Path

from services.curriculum_repository.repository import (
    curriculum_repository,
)

PROJECT_ROOT = Path(__file__).resolve().parents[2]

CURRICULUM_PATH = PROJECT_ROOT / "data_curricular"


class CurriculumProvider:
    """
    Provider oficial del currículo.
    """

    def __init__(self):

        self._initialized = False

    # ---------------------------------------------------------

    def initialize(self):

        if self._initialized:
            return

        curriculum_repository.initialize(
            CURRICULUM_PATH
        )

        self._initialized = True

    # ---------------------------------------------------------

    def reload(self):

        curriculum_repository.initialize(
            CURRICULUM_PATH
        )

    # ---------------------------------------------------------

    def summary(self):

        self.initialize()

        return curriculum_repository.summary()

    # ---------------------------------------------------------

    def statistics(self):

        self.initialize()

        return curriculum_repository.statistics()

    # ---------------------------------------------------------

    def modalities(self):

        self.initialize()

        return curriculum_repository.modalities()

    # ---------------------------------------------------------

    def courses(self):

        self.initialize()

        return curriculum_repository.courses()

    # ---------------------------------------------------------

    def subjects(self):

        self.initialize()

        return curriculum_repository.subjects()

    # ---------------------------------------------------------

    def by_modality(
        self,
        modality: str,
    ):

        self.initialize()

        return curriculum_repository.by_modality(
            modality
        )

    # ---------------------------------------------------------

    def by_course(
        self,
        course: str,
    ):

        self.initialize()

        return curriculum_repository.by_course(
            course
        )

    # ---------------------------------------------------------

    def by_subject(
        self,
        subject: str,
    ):

        self.initialize()

        return curriculum_repository.by_subject(
            subject
        )


    # ---------------------------------------------------------

    def find_modality(
        self,
        modality: str,
    ):

        self.initialize()

        return curriculum_repository.find_modality(
            modality
        )

    # ---------------------------------------------------------

    def find_course(
        self,
        course: str,
    ):

        self.initialize()

        return curriculum_repository.find_course(
            course
        )

    # ---------------------------------------------------------

    def find_subject(
        self,
        subject: str,
    ):

        self.initialize()

        return curriculum_repository.find_subject(
            subject
        )

    # ---------------------------------------------------------

    def search_modalities(
        self,
        text: str,
    ):

        self.initialize()

        return curriculum_repository.search_modalities(
            text
        )

    # ---------------------------------------------------------

    def search_courses(
        self,
        text: str,
    ):

        self.initialize()

        return curriculum_repository.search_courses(
            text
        )

    # ---------------------------------------------------------

    def search_subjects(
        self,
        text: str,
    ):

        self.initialize()

        return curriculum_repository.search_subjects(
            text
        )
    curriculum_provider = CurriculumProvider()