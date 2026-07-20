"""
===========================================================
AulaMind Enterprise 3.0

Curriculum Repository

Index

Versión 2

Adaptado al formato real del currículo AulaMind
===========================================================
"""

from __future__ import annotations

from collections import defaultdict
from typing import Any


class CurriculumIndex:
    """
    Índice curricular oficial.

    Construye índices para:

    - documentos
    - asignaturas
    - cursos
    - unidades
    - objetivos de aprendizaje (OA)
    """

    def __init__(self):

        self.clear()

    # ---------------------------------------------------------

    def clear(self):

        self.documents = []

        self.modalities = []

        self.subjects = []

        self.courses = []

        self.units = []

        self.objectives = []

        self._subjects = defaultdict(list)

        self._courses = defaultdict(list)

        self._units = defaultdict(list)

        self._objectives = defaultdict(list)

    # ---------------------------------------------------------

    def build(
        self,
        documents: list[Any],
    ):

        self.clear()

        for document in documents:

            if not isinstance(document, dict):
                continue

            self.documents.append(document)

            # ==========================================
            # Asignatura
            # ==========================================

            subject = (
                document.get("asignatura", "")
                .strip()
            )

            if subject:

                if subject not in self.subjects:
                    self.subjects.append(subject)

                self._subjects[subject].append(
                    document
                )

            # ==========================================
            # Curso
            # ==========================================

            course = (
                document.get("curso", "")
                .strip()
            )

            if course:

                if course not in self.courses:
                    self.courses.append(course)

                self._courses[course].append(
                    document
                )

            # ==========================================
            # Unidades
            # ==========================================

            for unit in document.get(
                "unidades",
                [],
            ):

                unit_name = (
                    unit.get("nombre", "")
                    .strip()
                )

                if unit_name:

                    if unit_name not in self.units:
                        self.units.append(
                            unit_name
                        )

                    self._units[
                        unit_name
                    ].append(unit)

                # ======================================
                # Objetivos de Aprendizaje
                # ======================================

                for oa in unit.get(
                    "oa",
                    [],
                ):

                    code = (
                        oa.get("codigo", "")
                        .strip()
                    )

                    if code:

                        if code not in self.objectives:
                            self.objectives.append(
                                code
                            )

                        self._objectives[
                            code
                        ].append(oa)

        self.subjects.sort()

        self.courses.sort()

        self.units.sort()

        self.objectives.sort()

    # ---------------------------------------------------------

    def by_subject(
        self,
        subject: str,
    ):

        return self._subjects.get(
            subject,
            [],
        )

    # ---------------------------------------------------------

    def by_course(
        self,
        course: str,
    ):

        return self._courses.get(
            course,
            [],
        )

    # ---------------------------------------------------------

    def by_unit(
        self,
        unit: str,
    ):

        return self._units.get(
            unit,
            [],
        )

    # ---------------------------------------------------------

    def by_objective(
        self,
        code: str,
    ):

        return self._objectives.get(
            code,
            [],
        )

    # ---------------------------------------------------------

    def statistics(self):

        return {

            "documents": len(
                self.documents
            ),

            "modalities": len(self.modalities),

            "courses": len(
                self.courses
            ),

            "subjects": len(
                self.subjects
            ),

            "units": len(
                self.units
            ),

            "objectives": len(
                self.objectives
            ),
        }