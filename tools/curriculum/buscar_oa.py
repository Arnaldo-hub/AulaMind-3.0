import re

with open(
    "txt/mat 1° básico.txt",
    "r",
    encoding="utf-8",
    errors="ignore"
) as f:

    texto = f.read()

for patron in [

    "OA 1",

    "OA1",

    "Objetivos de Aprendizaje",

    "Unidad 1"

]:

    pos = texto.find(
        patron
    )

    print(
        patron,
        "->",
        pos
    )