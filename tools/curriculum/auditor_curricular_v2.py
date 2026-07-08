import os
import json

CARPETA = "data_curricular"

print("\nAUDITORIA CURRICULAR\n")

for archivo in sorted(os.listdir(CARPETA)):

    if not archivo.endswith(".json"):
        continue

    ruta = os.path.join(
        CARPETA,
        archivo
    )

    try:

        with open(
            ruta,
            "r",
            encoding="utf-8"
        ) as f:

            data = json.load(f)

        unidades = data.get(
            "unidades",
            []
        )

        total_unidades = len(
            unidades
        )

        total_oa = 0

        for unidad in unidades:

            total_oa += len(
                unidad.get(
                    "oa",
                    []
                )
            )

        estado = "LISTO"

        if total_oa < 5:

            estado = "INCOMPLETO"

        print(
            f"{archivo}"
        )

        print(
            f"  Unidades: {total_unidades}"
        )

        print(
            f"  OA: {total_oa}"
        )

        print(
            f"  Estado: {estado}"
        )

        print()

    except Exception as e:

        print(
            f"ERROR -> {archivo}"
        )

        print(e)