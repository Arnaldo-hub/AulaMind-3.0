import os
import json

CARPETA = "data_curricular"

for archivo in os.listdir(CARPETA):

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

        total_oa = 0

        for unidad in data.get(
            "unidades",
            []
        ):

            total_oa += len(
                unidad.get(
                    "oa",
                    []
                )
            )

        if total_oa < 3:

            print(
                f"REVISAR -> {archivo} ({total_oa} OA)"
            )

        else:

            print(
                f"OK -> {archivo} ({total_oa} OA)"
            )

    except Exception as e:

        print(
            f"ERROR -> {archivo}"
        )

        print(e)