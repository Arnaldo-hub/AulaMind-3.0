import os
import json

ORIGEN = "data_oficial"
DESTINO = "data"

os.makedirs(
    DESTINO,
    exist_ok=True
)

curriculos = {}

for archivo in os.listdir(ORIGEN):

    if not archivo.endswith(".json"):
        continue

    ruta = os.path.join(
        ORIGEN,
        archivo
    )

    with open(
        ruta,
        "r",
        encoding="utf-8"
    ) as f:

        data = json.load(f)

    asignatura = data.get(
        "asignatura",
        "general"
    ).lower()

    curso = data.get(
        "curso",
        "curso"
    )

    if asignatura not in curriculos:

        curriculos[asignatura] = {}

    curriculos[asignatura][curso] = {

        "unidades": [

            {
                "nombre": "Unidad 1",

                "oa": data.get(
                    "oa",
                    []
                )
            }

        ]

    }

for asignatura, contenido in curriculos.items():

    ruta_salida = os.path.join(

        DESTINO,

        f"{asignatura}.json"

    )

    with open(

        ruta_salida,

        "w",

        encoding="utf-8"

    ) as salida:

        json.dump(

            contenido,

            salida,

            ensure_ascii=False,

            indent=4

        )

    print(
        f"Generado: {ruta_salida}"
    )

print(
    "\nProceso finalizado"
)