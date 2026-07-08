import os
import re

TXT_DIR = "txt"

PATRON = r"OA\s*\d+"

for archivo in sorted(os.listdir(TXT_DIR)):

    if not archivo.lower().startswith("mat"):
        continue

    if not archivo.endswith(".txt"):
        continue

    ruta = os.path.join(
        TXT_DIR,
        archivo
    )

    with open(
        ruta,
        "r",
        encoding="utf-8",
        errors="ignore"
    ) as f:

        texto = f.read()

    encontrados = re.findall(
        PATRON,
        texto,
        flags=re.IGNORECASE
    )

    unicos = []

    for x in encontrados:

        x = x.upper().strip()

        if x not in unicos:

            unicos.append(x)

    print()

    print(archivo)

    print(
        f"OA encontrados: {len(unicos)}"
    )

    print(
        unicos[:20]
    )