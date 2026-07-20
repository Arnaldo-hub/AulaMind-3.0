"""
===========================================================
AulaMind Enterprise 3.0

Curriculum Repository

Search Engine

Sprint 9.6.10
===========================================================

Motor de búsqueda curricular.

Responsabilidades

- Buscar modalidades
- Buscar cursos
- Buscar asignaturas
- Buscar documentos

No carga datos.

No construye índices.

Trabaja exclusivamente sobre CurriculumIndex.
"""

from __future__ import annotations

from services.curriculum_repository.index import CurriculumIndex


class CurriculumSearch:
    """
    Motor oficial de búsqueda del currículo.
    """

    def __init__(
        self,
        index: CurriculumIndex,
    ):

        self.index = index

    # ---------------------------------------------------------

    def modality(
        self,
        name: str,
    ):

        return self.index.by_modality(
            name
        )

    # ---------------------------------------------------------

    def course(
        self,
        name: str,
    ):

        return self.index.by_course(
            name
        )

    # ---------------------------------------------------------

    def subject(
        self,
        name: str,
    ):

        return self.index.by_subject(
            name
        )

    # ---------------------------------------------------------

    def contains_course(
        self,
        name: str,
    ) -> bool:

        return name in self.index.courses

    # ---------------------------------------------------------

    def contains_subject(
        self,
        name: str,
    ) -> bool:

        return name in self.index.subjects

    # ---------------------------------------------------------

    def contains_modality(
        self,
        name: str,
    ) -> bool:

        return name in self.index.modalities

    # ---------------------------------------------------------

    def courses_like(
        self,
        text: str,
    ):

        text = text.lower()

        return [

            course

            for course in self.index.courses

            if text in course.lower()

        ]

    # ---------------------------------------------------------

    def subjects_like(
        self,
        text: str,
    ):

        text = text.lower()

        return [

            subject

            for subject in self.index.subjects

            if text in subject.lower()

        ]

    # ---------------------------------------------------------

    def modalities_like(
        self,
        text: str,
    ):

        text = text.lower()

        return [

            modality

            for modality in self.index.modalities

            if text in modality.lower()

        ]