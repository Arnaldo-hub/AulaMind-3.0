import os
import json
from openai import OpenAI

# =========================================
# CONFIG
# =========================================

api_key = os.getenv(
    "OPENAI_API_KEY"
)

client = OpenAI(
    api_key=api_key
)

TXT_DIR = "txt"

SALIDA_DIR = "data_curricular"

os.makedirs(
    SALIDA_DIR,
    exist_ok=True
)

# =========================================
# LIMPIAR TEXTO
# =========================================

def preparar_texto(texto):

    pos = texto.find(
        "OA 1"
    )

    if pos != -1:

        inicio = max(
            0,
            pos - 5000
        )

        return texto[inicio:]

    return texto

# =========================================
# IA
# =========================================

def generar_json(texto):

    prompt = f"""
Eres especialista curricular MINEDUC Chile.

Extrae solamente:

- asignatura
- curso
- unidades
- objetivos de aprendizaje

Devuelve EXCLUSIVAMENTE JSON.

Formato:

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
                "role":"user",
                "content":prompt
            }
        ],

        temperature=0

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

# =========================================
# PROCESAR
# =========================================

def procesar_archivo(nombre):

    ruta = os.path.join(
        TXT_DIR,
        nombre
    )

    print(
        f"\nProcesando: {nombre}"
    )

    with open(
        ruta,
        "r",
        encoding="utf-8",
        errors="ignore"
    ) as f:

        texto = f.read()

    texto = preparar_texto(
        texto
    )

    data = generar_json(
        texto
    )

    nombre_salida = nombre.replace(
        ".txt",
        ".json"
    )

    salida = os.path.join(
        SALIDA_DIR,
        nombre_salida
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
        f"Generado: {salida}"
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

        if x.lower().startswith(
            "mat"
        )

        and x.endswith(
            ".txt"
        )

    ]

    print(
        f"Matemática encontrados: {len(archivos)}"
    )

    for archivo in archivos:

        try:

            procesar_archivo(
                archivo
            )

        except Exception as e:

            print(
                f"ERROR {archivo}: {e}"
            )

    print(
        "\nProceso terminado"
    )

if __name__ == "__main__":
    main()