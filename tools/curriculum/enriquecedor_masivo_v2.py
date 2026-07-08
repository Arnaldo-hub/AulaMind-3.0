import os
import json
import time

from openai import OpenAI

# =====================================
# CONFIG
# =====================================

api_key = os.getenv(
    "OPENAI_API_KEY"
)

client = OpenAI(
    api_key=api_key
)

CARPETA_ENTRADA = "data_curricular"

CARPETA_SALIDA = "data_pedagogica"

os.makedirs(
    CARPETA_SALIDA,
    exist_ok=True
)

# =====================================
# OA -> PEDAGOGIA
# =====================================

def enriquecer_oa(
    codigo,
    descripcion
):

    prompt = f"""
Eres experto curricular MINEDUC Chile.

Objetivo:

Código:
{codigo}

Descripción:
{descripcion}

Genera:

- 5 indicadores
- 5 habilidades
- 5 estrategias de evaluación
- 3 actividades de inicio
- 5 actividades de desarrollo
- 3 actividades de cierre
- 5 adecuaciones NEE
- 5 recursos

Devuelve SOLO JSON.

Formato:

{{
    "indicadores": [],
    "habilidades": [],
    "evaluacion": [],
    "actividades": {{
        "inicio": [],
        "desarrollo": [],
        "cierre": []
    }},
    "adaptaciones_nee": [],
    "recursos": []
}}
"""

    respuesta = client.chat.completions.create(

        model="gpt-4.1-mini",

        messages=[

            {
                "role": "user",
                "content": prompt
            }

        ],

        temperature=0.3

    )

    contenido = (
        respuesta
        .choices[0]
        .message
        .content
    )

    inicio = contenido.find("{")

    fin = contenido.rfind("}") + 1

    contenido = contenido[inicio:fin]

    return json.loads(
        contenido
    )

# =====================================
# VALIDAR
# =====================================

def curso_listo(data):

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

    return total_oa >= 5

# =====================================
# PROCESAR CURSO
# =====================================

def procesar_archivo(nombre):

    ruta = os.path.join(
        CARPETA_ENTRADA,
        nombre
    )

    with open(
        ruta,
        "r",
        encoding="utf-8"
    ) as f:

        data = json.load(f)

    if not curso_listo(data):

        print(
            f"SALTADO -> {nombre}"
        )

        return

    print(
        f"\nENRIQUECIENDO -> {nombre}"
    )

    for unidad in data.get(
        "unidades",
        []
    ):

        for oa in unidad.get(
            "oa",
            []
        ):

            print(
                f"   {oa['codigo']}"
            )

            try:

                extra = enriquecer_oa(

                    oa["codigo"],

                    oa["descripcion"]

                )

                oa.update(
                    extra
                )

                time.sleep(1)

            except Exception as e:

                print(
                    f"ERROR OA {oa['codigo']}"
                )

                print(e)

    salida = os.path.join(
        CARPETA_SALIDA,
        nombre
    )

    with open(
        salida,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(

            data,

            f,

            ensure_ascii=False,

            indent=4

        )

    print(
        f"GENERADO -> {salida}"
    )

# =====================================
# MAIN
# =====================================

def main():

    archivos = sorted(

        [

            x

            for x in os.listdir(
                CARPETA_ENTRADA
            )

            if x.endswith(
                ".json"
            )

        ]

    )

    print(
        f"Cursos encontrados: {len(archivos)}"
    )

    for archivo in archivos:

        procesar_archivo(
            archivo
        )

    print(
        "\nFINALIZADO"
    )

if __name__ == "__main__":
    main()