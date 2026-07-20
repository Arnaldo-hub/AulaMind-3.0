"""
===========================================================
AulaMind Enterprise 3.0

Curriculum Auditor Test

Semana 6.2
===========================================================
"""

from pathlib import Path

from services.curriculum_auditor.auditor import (
    curriculum_auditor,
)


def main():

    root = Path(__file__).resolve().parents[1]

    curriculum = root / "data_curricular"

    print()

    print("=" * 60)
    print("AulaMind Curriculum Auditor")
    print("=" * 60)
    print()

    report = curriculum_auditor.audit(curriculum)

    print("Versión")
    print("--------")
    print(report["version"])
    print()

    print("Documentos")
    print("-----------")
    print(report["summary"]["documents"])
    print()

    print("Cobertura")
    print("----------")
    print(f'{report["summary"]["coverage"]}%')
    print()

    print("Completitud promedio")
    print("--------------------")
    print(f'{report["summary"]["average_completeness"]}%')
    print()

    print("Estados")
    print("--------")

    for status, total in sorted(report["status"].items()):

        print(f"{status:25} {total}")

    print()

    print("Modalidades")
    print("-----------")

    for modality, total in report["modalities"]:

        print(f"{modality:20} {total}")

    print()

    print("=" * 60)
    print("CURRICULUM AUDITOR OK")
    print("=" * 60)


if __name__ == "__main__":

    main()