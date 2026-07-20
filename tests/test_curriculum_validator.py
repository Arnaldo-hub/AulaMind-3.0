from services.curriculum_validator.validator import (
    curriculum_validator,
)


def main():

    document = {

        "modalidad": "regular",

        "curso": "1° básico",

        "asignatura": "Artes Visuales",

        "nivel": "Educación Básica",

        "unidades": [

            {

                "nombre": "Unidad 1",

                "oa": [

                    "OA1",

                    "OA2",

                ]

            }

        ]

    }

    result = curriculum_validator.validate_document(

        "demo.json",

        document,

    )

    print(result.to_dict())

    assert result is not None

    print()

    print("=" * 60)

    print("Curriculum Validator OK")

    print("=" * 60)


if __name__ == "__main__":
    main()