from services.curriculum_validator.schema_validator import (
    schema_validator,
)


def main():

    document = {

        "modalidad": "regular",

        "curso": "1° básico",

        "asignatura": "Artes Visuales",

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

    result = schema_validator.validate(

        "demo.json",

        document,

    )

    print(result.to_dict())

    assert result.valid

    print()

    print("Schema Validator OK")


if __name__ == "__main__":
    main()