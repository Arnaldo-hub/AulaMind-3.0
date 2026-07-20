"""
===========================================================
AulaMind Enterprise 3.0

Curriculum Validator

Validación completa del currículo

Semana 5A.7
===========================================================
"""

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from services.curriculum_validator.validator import (
    curriculum_validator,
)

from services.curriculum_validator.coverage_report import (
    coverage_report,
)


# =========================================================


def main():

    curriculum_root = ROOT / "data_curricular"

    print()

    print("=" * 70)
    print("AulaMind Curriculum Validator")
    print("=" * 70)

    print()

    print("Analizando:")

    print(curriculum_root)

    print()

    summary = curriculum_validator.validate_directory(
        curriculum_root
    )

    coverage_report.print_console(summary)

    print()

    print("=" * 70)
    print("DOCUMENTOS PRIORITARIOS")
    print("=" * 70)

    print()

    priority = coverage_report.priority_list(
        summary.results
    )

    total = 0

    for result in priority:

        if result.estado.value == "VALID":
            continue

        total += 1

        print(
            f"[{result.estado.value}] "
            f"{result.modalidad} | "
            f"{result.curso} | "
            f"{result.asignatura}"
        )

        for error in result.errores:

            print(
                f"   ERROR : {error.code} -> {error.message}"
            )

        for warning in result.advertencias:

            print(
                f"   WARNING : {warning.code} -> {warning.message}"
            )

        print()

    print("=" * 70)

    print(f"Documentos con observaciones : {total}")

    print(f"Cobertura curricular         : {summary.coverage}%")

    print("=" * 70)

    print()

    print("VALIDACIÓN CURRICULAR FINALIZADA")


# =========================================================

if __name__ == "__main__":
    main()