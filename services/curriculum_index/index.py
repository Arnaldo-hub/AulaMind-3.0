"""
===========================================================
AulaMind Enterprise 3.0

Curriculum Index

Sprint 9.6.4
===========================================================

Construye un índice de búsqueda sobre el AuditReport
para permitir consultas rápidas desde la API.
"""

from __future__ import annotations

from collections import defaultdict

from services.curriculum_auditor.models import AuditReport


class CurriculumIndex:
    """
    Índice curricular.
    """

    def build(self, report: AuditReport):

        data = {
            "modalities": set(),
            "courses": set(),
            "subjects": set(),
            "by_course": defaultdict(list),
            "by_subject": defaultdict(list),
        }

        for document in report.documents:

            modality = document.modalidad
            course = document.curso
            subject = document.asignatura

            if modality:
                data["modalities"].add(modality)

            if course:
                data["courses"].add(course)

            if subject:
                data["subjects"].add(subject)

            if course:
                data["by_course"][course].append(document)

            if subject:
                data["by_subject"][subject].append(document)

        data["modalities"] = sorted(data["modalities"])
        data["courses"] = sorted(data["courses"])
        data["subjects"] = sorted(data["subjects"])

        return data


curriculum_index = CurriculumIndex()