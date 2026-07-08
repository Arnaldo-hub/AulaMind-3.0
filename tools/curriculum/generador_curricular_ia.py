import os
import json
import re

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

TXT_DIR = "txt"

SALIDA_DIR = "data_oficial"

os.makedirs(
    SALIDA_DIR,
    exist_ok=True
)

# =========================================
# LIMPIAR TEXTO
# =========================================

def limpiar_texto_curricular(texto):

    pos = texto.find("OA 1")

    if pos != -1:

        inicio = max(
            0,
            pos - 5000
        )

        return texto[inicio:]

    return texto


# =========================================
# GENERAR JSON IA
# =========================================

def generar_json_curricular(texto):

    prompt = f"""
Eres un experto curricular del MINEDUC Chile.

Analiza el siguiente texto curricular.

Extrae exclusivamente:

1. Asignatura
2. Curso
3. Unidades
4. Objetivos de Aprendizaje (OA)

Reglas:

- NO agregues explicaciones.
- NO agregues comentarios.
- NO agregues markdown.
- Devuelve SOLO JSON válido.
- Mantén exactamente el código OA.
- Cada OA debe tener:
    - codigo
    - descripcion

Formato esperado:

{{
    "asignatura":"",
    "curso":"",
    "unidades":[
        {{
            "nombre":"",
            "oa":[
                {{
                    "codigo":"OA 1",
                    "descripcion":""
                }}
            ]
        }}
    ]
}}

Texto:

{texto[:60000]}
"""

    respuesta = client.chat.completions.create(

        model="gpt-4.1-mini",

        messages=[

            {
                "role": "user",
                "content": prompt
            }

        ],

        temperature=0

    )

    return respuesta.choices[0].message.content


# =========================================
# PROCESAR ARCHIVO
# =========================================

def procesar_archivo(nombre_archivo):

    ruta = os.path.join(
        TXT_DIR,
        nombre_archivo
    )

    print(
        f"\nProcesando: {nombre_archivo}"
    )

    with open(

        ruta,
        "r",
        encoding="utf-8",
        errors="ignore"

    ) as f:

        texto = f.read()

    texto = limpiar_texto_curricular(
        texto
    )

    resultado = generar_json_curricular(
        texto
    )

    salida = os.path.join(

        SALIDA_DIR,

        nombre_archivo.replace(
            ".txt",
            ".json"
        )

    )

    with open(

        salida,
        "w",
        encoding="utf-8"

    ) as f:

        f.write(
            resultado
        )

    print(
        f"JSON generado: {salida}"
    )


# =========================================
# MAIN
# =========================================

def main():

    archivos = [

        x

        for x in os.listdir(
            TXT_DIR
        )

        if x.endswith(
            ".txt"
        )

    ]

    print(
        f"TXT encontrados: {len(archivos)}"
    )

    # =====================================
    # PRUEBA SOLO CON MATEMATICA 1°
    # =====================================

    prueba = [

        "mat 1° básico.txt"

    ]

    for archivo in prueba:

        if archivo in archivos:

            procesar_archivo(
                archivo
            )

    print(
        "\nProceso finalizado"
    )


if __name__ == "__main__":

    main()