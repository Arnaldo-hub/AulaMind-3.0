from services.curriculum_validator.duplicate_detector import (
    duplicate_detector,
)


def main():

    duplicate_detector.reset()

    document1 = {

        "modalidad": "regular",

        "curso": "1° básico",

        "asignatura": "Artes Visuales",

    }

    document2 = {

        "modalidad": "regular",

        "curso": "1° básico",

        "asignatura": "Artes Visuales",

    }

    result1 = duplicate_detector.validate(

        "doc1.json",

        document1,

    )

    result2 = duplicate_detector.validate(

        "doc2.json",

        document2,

    )

    assert result1.valid

    assert result2.estado.value == "DUPLICATE"

    print()

    print(result1.to_dict())

    print()

    print(result2.to_dict())

    print()

    print("=" * 60)

    print("Duplicate Detector OK")

    print("=" * 60)


if __name__ == "__main__":
    main()