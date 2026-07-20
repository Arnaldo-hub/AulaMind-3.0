from services.curriculum_validator.coverage_report import (
    coverage_report,
)

from services.curriculum_validator.models import (
    ValidationResult,
    ValidationStatus,
)


def main():

    results = []

    for i in range(5):

        r = ValidationResult(

            path=f"doc{i}.json",

            modalidad="regular",

            curso="1° básico",

            asignatura=f"Asig {i}",

        )

        results.append(r)

    results[1].set_status(

        ValidationStatus.INCOMPLETE

    )

    results[2].set_status(

        ValidationStatus.DUPLICATE

    )

    results[3].set_status(

        ValidationStatus.REFERENCE_REQUIRED

    )

    results[4].set_status(

        ValidationStatus.SCHEMA_ERROR

    )

    summary = coverage_report.generate(

        results

    )

    coverage_report.print_console(

        summary

    )

    print(

        coverage_report.to_dict(summary)

    )

    assert summary.total == 5

    assert summary.valid == 1

    assert summary.coverage == 20.0

    print()

    print("Coverage Report OK")


if __name__ == "__main__":
    main()