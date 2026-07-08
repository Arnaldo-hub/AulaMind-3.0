import os
import json

from openai import OpenAI

# =========================================
# CONFIGURACION
# =========================================

api_key = os.getenv(
    "OPENAI_API_KEY"
)

client = OpenAI(
    api_key=api_key
)

ARCHIVO_ENTRADA = (
    "data_oficial/mat 1° básico.json"
)

ARCHIVO_SALIDA = (
    "data_oficial/mat 1° básico_enriquecido.json"
)

# =========================================
# ENRIQUECER OA
# =========================================

def enriquecer_oa(
    codigo,
    descripcion
):

    prompt = f"""
Eres experto en currículo MINEDUC Chile.

Para el siguiente Objetivo de Aprendizaje:

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

IMPORTANTE:

Devuelve EXCLUSIVAMENTE JSON válido.

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

    print("\n===================")
    print("RESPUESTA IA")
    print("===================\n")
    print(contenido)
    print("\n")

    try:

        inicio = contenido.find("{")

        fin = contenido.rfind("}") + 1

        contenido_json = (
            contenido[inicio:fin]
        )

        return json.loads(
            contenido_json
        )

    except Exception as e:

        print(
            f"\nERROR JSON: {e}"
        )

        return {

            "indicadores": [],

            "habilidades": [],

            "evaluacion": [],

            "actividades": {

                "inicio": [],

                "desarrollo": [],

                "cierre": []

            },

            "adaptaciones_nee": [],

            "recursos": []

        }


# =========================================
# MAIN
# =========================================

def main():

    print(
        f"Leyendo: {ARCHIVO_ENTRADA}"
    )

    with open(

        ARCHIVO_ENTRADA,
        "r",
        encoding="utf-8"

    ) as f:

        data = json.load(f)

    total_oa = 0

    for unidad in data.get(
        "unidades",
        []
    ):

        for oa in unidad.get(
            "oa",
            []
        ):

            total_oa += 1

            print(
                f"\nEnriqueciendo {oa['codigo']}..."
            )

            extra = enriquecer_oa(

                oa["codigo"],

                oa["descripcion"]

            )

            oa.update(
                extra
            )

    print(
        f"\nOA procesados: {total_oa}"
    )

    with open(

        ARCHIVO_SALIDA,
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
        f"\nGenerado: {ARCHIVO_SALIDA}"
    )


if __name__ == "__main__":

    main()