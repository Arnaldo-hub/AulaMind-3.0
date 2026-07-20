"""
============================================================
AulaMind Enterprise 3.0

Tests

Curriculum Repository

Sprint 9.8.1
============================================================
"""

from pathlib import Path

from services.curriculum_repository.repository import (
    curriculum_repository,
)

PROJECT_ROOT = Path(__file__).resolve().parents[1]

CURRICULUM_PATH = PROJECT_ROOT / "data_curricular"


def main():

    print()

    print("=" * 60)
    print("AulaMind Curriculum Repository")
    print("=" * 60)

    curriculum_repository.initialize(
        CURRICULUM_PATH
    )

    # ---------------------------------------------------------
    # Estado
    # ---------------------------------------------------------

    print()
    print("Estado")
    print("-" * 20)

    print(
        "Inicializado :",
        curriculum_repository.loaded,
    )

    print(
        "Ruta :",
        curriculum_repository.root,
    )

    # ---------------------------------------------------------
    # Estadísticas
    # ---------------------------------------------------------

    statistics = curriculum_repository.statistics()

    print()
    print("Estadísticas")
    print("-" * 20)

    print(
        "Documentos :",
        statistics["documents"],
    )

    print(
        "Modalidades :",
        statistics["modalities"],
    )

    print(
        "Cursos :",
        statistics["courses"],
    )

    print(
        "Asignaturas :",
        statistics["subjects"],
    )

    # ---------------------------------------------------------
    # Colecciones
    # ---------------------------------------------------------

    print()
    print("Colecciones")
    print("-" * 20)

    print(
        "Modalidades:",
        len(
            curriculum_repository.modalities()
        ),
    )

    print(
        "Cursos:",
        len(
            curriculum_repository.courses()
        ),
    )

    print(
        "Asignaturas:",
        len(
            curriculum_repository.subjects()
        ),
    )

    # ---------------------------------------------------------
    # Búsquedas
    # ---------------------------------------------------------

    print()
    print("Búsquedas")
    print("-" * 20)

    if curriculum_repository.courses():

        first_course = (
            curriculum_repository.courses()[0]
        )

        print(
            "Primer curso:",
            first_course,
        )

        print(
            "Documentos:",
            len(
                curriculum_repository.find_course(
                    first_course
                )
            ),
        )

    if curriculum_repository.subjects():

        first_subject = (
            curriculum_repository.subjects()[0]
        )

        print(
            "Primera asignatura:",
            first_subject,
        )

        print(
            "Documentos:",
            len(
                curriculum_repository.find_subject(
                    first_subject
                )
            ),
        )

    # ---------------------------------------------------------
    # Summary
    # ---------------------------------------------------------

    print()
    print("Summary")
    print("-" * 20)

    print(
        curriculum_repository.summary()
    )

    print()

    print("=" * 60)
    print("CURRICULUM REPOSITORY OK")
    print("=" * 60)


if __name__ == "__main__":
    main()