import os
import json

CARPETA = "data_oficial"

eliminados = 0

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

            json.load(f)

    except Exception:

        os.remove(ruta)

        eliminados += 1

        print(
            f"ELIMINADO -> {archivo}"
        )

print(
    f"\nTotal eliminados: {eliminados}"
)