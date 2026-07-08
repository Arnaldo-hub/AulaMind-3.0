import json
import os

# =========================================
# ARCHIVO
# =========================================

BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

RUTA = os.path.join(
    BASE_DIR,
    "data",
    "matematica.json"
)

# =========================================
# LEER JSON
# =========================================

with open(
    RUTA,
    "r",
    encoding="utf-8"
) as archivo:

    data = json.load(archivo)

# =========================================
# ENRIQUECER 1° BÁSICO
# =========================================

curso = data.get(
    "1° Básico",
    {}
)

unidades = curso.get(
    "unidades",
    []
)

if len(unidades) > 0:

    unidades[0]["nombre"] = (
        "Unidad 1: Números y Operaciones"
    )

    unidades[0]["proposito"] = (
        "Desarrollar la comprensión de números hasta el 20, promoviendo habilidades de conteo, representación y resolución de problemas."
    )

    unidades[0]["oa"] = [

        {
            "codigo": "OA 1",

            "descripcion":
            "Contar números del 0 al 20 de 1 en 1, de 2 en 2 y hacia atrás."
        },

        {
            "codigo": "OA 2",

            "descripcion":
            "Leer y representar números hasta el 20 en forma concreta, pictórica y simbólica."
        },

        {
            "codigo": "OA 3",

            "descripcion":
            "Comparar y ordenar números del 0 al 20."
        }

    ]

    unidades[0]["habilidades"] = [

        "Contar",
        "Representar",
        "Comparar",
        "Resolver problemas"

    ]

    unidades[0]["actitudes"] = [

        "Participar activamente",
        "Perseverar en el trabajo matemático",
        "Comunicar ideas matemáticas"

    ]

# =========================================
# GUARDAR JSON
# =========================================

with open(
    RUTA,
    "w",
    encoding="utf-8"
) as archivo:

    json.dump(

        data,
        archivo,
        ensure_ascii=False,
        indent=2

    )

print(
    "✅ Matemática 1° Básico enriquecido"
<<<<<<< HEAD
)
=======
)
>>>>>>> a39ab736936a9ccd970b444c197cef0b2e6a3d50
