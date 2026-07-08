import os
import re
import json

TXT_DIR = "txt"
SALIDA_DIR = "data_oficial"

os.makedirs(SALIDA_DIR, exist_ok=True)


def detectar_asignatura(nombre_archivo):

    nombre = nombre_archivo.lower()

    mapa = {
        "mat": "Matemática",
        "leng": "Lenguaje y Comunicación",
        "hist": "Historia, Geografía y Ciencias Sociales",
        "ciencias": "Ciencias Naturales",
        "ingles": "Inglés",
        "inglés": "Inglés",
        "musica": "Música",
        "música": "Música",
        "tecnol": "Tecnología",
        "orient": "Orientación",
        "efi": "Educación Física y Salud",
        "educ. física": "Educación Física y Salud",
        "artes": "Artes Visuales"
    }

    for clave, valor in mapa.items():
        if clave in nombre:
            return valor

    return "Asignatura no detectada"


def detectar_curso(nombre_archivo):

    patrones = [
        r'(\d+°\s*básico)',
        r'(\d+°\s*medio)',
        r'(kinder)',
        r'(pre kinder)'
    ]

    nombre = nombre_archivo.lower()

    for patron in patrones:

        m = re.search(
            patron,
            nombre,
            re.IGNORECASE
        )

        if m:
            return m.group(1)

    return "Curso no detectado"


def extraer_oa(texto):

    patron = re.compile(
        r'\b(OA\s+\d+)\b',
        re.IGNORECASE
    )

    coincidencias = list(
        patron.finditer(texto)
    )

    oa_lista = []

    for i in range(
        len(coincidencias)
    ):

        inicio = coincidencias[i].start()

        if i < len(coincidencias) - 1:

            fin = coincidencias[
                i + 1
            ].start()

        else:

            fin = len(texto)

        bloque = texto[
            inicio:fin
        ].strip()

        lineas = [

            l.strip()

            for l in bloque.splitlines()

            if l.strip()

        ]

        if len(lineas) < 2:

            continue

        codigo = lineas[0]

        descripcion = " ".join(
            lineas[1:8]
        )

        descripcion = re.sub(
            r'\s+',
            ' ',
            descripcion
        )

        if len(descripcion) < 20:

            continue

        oa_lista.append({

            "codigo": codigo,

            "descripcion":
            descripcion

        })

    return oa_lista


def procesar_archivo(ruta_txt):

    nombre = os.path.basename(
        ruta_txt
    )

    with open(
        ruta_txt,
        "r",
        encoding="utf-8",
        errors="ignore"
    ) as f:

        texto = f.read()

    asignatura = detectar_asignatura(
        nombre
    )

    curso = detectar_curso(
        nombre
    )

    oa = extraer_oa(
        texto
    )

    estructura = {
        "asignatura": asignatura,
        "curso": curso,
        "total_oa": len(oa),
        "oa": oa
    }

    nombre_salida = nombre.replace(
        ".txt",
        ".json"
    )

    ruta_json = os.path.join(
        SALIDA_DIR,
        nombre_salida
    )

    with open(
        ruta_json,
        "w",
        encoding="utf-8"
    ) as salida:

        json.dump(
            estructura,
            salida,
            ensure_ascii=False,
            indent=4
        )

    print(
        f"OK -> {nombre_salida}"
    )


def main():

    archivos = [
        a for a in os.listdir(TXT_DIR)
        if a.endswith(".txt")
    ]

    print(
        f"\nProcesando {len(archivos)} archivos...\n"
    )

    for archivo in archivos:

        ruta = os.path.join(
            TXT_DIR,
            archivo
        )

        try:

            procesar_archivo(
                ruta
            )

        except Exception as e:

            print(
                f"ERROR {archivo}: {e}"
            )

    print(
        "\nProceso finalizado"
    )


if __name__ == "__main__":
    main()