from services.curriculum_validator.reference_checker import (
    reference_checker,
)


def main():

    document = {

        "modalidad": "regular",

        "curso": "1° básico",

        "asignatura": "Artes Visuales",

        "nivel": "Educación Básica",

    }

    result = reference_checker.validate(

        "demo.json",

        document,

    )

    print(result.to_dict())

    assert result.estado.value == "REFERENCE_REQUIRED"

    print()

    print("=" * 60)

    print("Reference Checker OK")

    print("=" * 60)


if __name__ == "__main__":
    main()