"""
===========================================================
AulaMind Enterprise 3.0

Curriculum Auditor

Statistics Engine

Semana 6.3
===========================================================
"""

from __future__ import annotations

from collections import Counter
from typing import Iterable


class StatisticsEngine:
    """
    Motor de estadísticas del Curriculum Auditor.

    Su única responsabilidad es transformar una colección
    de ValidationResult en estadísticas ejecutivas.
    """

    VERSION = "6.3"

    # ---------------------------------------------------------

    def calculate(
        self,
        results: Iterable,
    ) -> dict:

        status_counter = Counter()
        modality_counter = Counter()
        course_counter = Counter()
        subject_counter = Counter()

        completeness_scores = []

        valid_documents = []

        incomplete_documents = []

        duplicate_documents = []

        total = 0

        for result in results:

            total += 1

            estado = getattr(
                result.estado,
                "value",
                str(result.estado),
            )

            status_counter[estado] += 1

            modalidad = getattr(
                result,
                "modalidad",
                "",
            )

            if modalidad:
                modality_counter[modalidad] += 1

            curso = getattr(
                result,
                "curso",
                "",
            )

            if curso:
                course_counter[curso] += 1

            asignatura = getattr(
                result,
                "asignatura",
                "",
            )

            if asignatura:
                subject_counter[asignatura] += 1

            metadata = getattr(
                result,
                "metadata",
                {},
            )

            score = (
                metadata
                .get("completeness", {})
                .get("score", 0)
            )

            completeness_scores.append(score)

            document = {
                "path": result.path,
                "modalidad": modalidad,
                "curso": curso,
                "asignatura": asignatura,
                "score": score,
                "estado": estado,
            }

            if estado == "VALID":
                valid_documents.append(document)

            elif estado == "INCOMPLETE":
                incomplete_documents.append(document)

            elif estado == "DUPLICATE":
                duplicate_documents.append(document)

        coverage = 0.0

        if total:

            coverage = round(

                status_counter.get("VALID", 0)
                * 100
                / total,

                2,

            )

        average = 0.0

        if completeness_scores:

            average = round(

                sum(completeness_scores)
                / len(completeness_scores),

                2,

            )

        valid_documents.sort(
            key=lambda x: x["score"],
            reverse=True,
        )

        incomplete_documents.sort(
            key=lambda x: x["score"],
        )

        return {

            "documents": total,

            "coverage": coverage,

            "average_completeness": average,

            "status": dict(status_counter),

            "modalities": dict(modality_counter),

            "courses": dict(course_counter),

            "subjects": dict(subject_counter),

            "top_valid": valid_documents[:20],

            "top_incomplete": incomplete_documents[:20],

            "duplicates": duplicate_documents,

        }

    # ---------------------------------------------------------

    def statistics(self):

        return {

            "module": "Statistics Engine",

            "version": self.VERSION,

            "outputs": [

                "coverage",

                "average_completeness",

                "status",

                "modalities",

                "courses",

                "subjects",

                "top_valid",

                "top_incomplete",

                "duplicates",

            ],

        }


statistics_engine = StatisticsEngine()