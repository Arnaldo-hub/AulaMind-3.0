"""
===========================================================
AulaMind Enterprise 3.0
services/format_rules.py
-----------------------------------------------------------

Reglas de formato profesional para TODAS las salidas IA
de la plataforma (v3.7).

Capa 1 (prevencion): with_format_rules() agrega las reglas
al system prompt de cualquier generacion.

Capa 2 (saneamiento): clean_ai_text() elimina cualquier
residuo de sintaxis markdown del texto devuelto por la IA,
sin importar que prompt se uso.

Se aplica desde OpenAIService.generate(), punto unico por
donde pasan EvaluationService, PlanningService, PIEService,
FonoaudiologiaService, RubricService, GuideService y
ToolsService.

Autor:
Biotecno Chile
===========================================================
"""

import re

FORMAT_MARKER = "REGLAS DE FORMATO PROFESIONAL"

# ------------------------------------------------------
# REGLAS INYECTADAS AL SYSTEM PROMPT
# ------------------------------------------------------

PROFESSIONAL_FORMAT = """

REGLAS DE FORMATO PROFESIONAL (obligatorias, sin excepcion):
- NO uses sintaxis markdown: prohibido **, ##, ###, ---,
  __, ` y listas con asteriscos.
- Estructura el documento en TEXTO PLANO: titulos en
  MAYUSCULAS y lineas en blanco entre secciones.
- NO uses lineas separadoras (---, ===, ***); separa las
  secciones solo con lineas en blanco.
- NO repitas el encabezado (profesor, asignatura, curso,
  fecha, colegio): la plataforma ya lo agrega
  automaticamente. Comienza directo con el contenido.
- Numera las preguntas con punto (1. 2. 3.) y las
  alternativas con letra (a) b) c)).
- NO incluyas notas, aclaraciones ni ofertas de ayuda al
  final del documento.
- Entrega SOLO el contenido final solicitado.
"""


def with_format_rules(system_prompt):
    """
    Agrega las reglas de formato profesional al system
    prompt. Idempotente: si ya estan presentes, no las
    duplica.
    """
    if FORMAT_MARKER in (system_prompt or ""):
        return system_prompt
    return (system_prompt or "") + PROFESSIONAL_FORMAT


# ------------------------------------------------------
# SANEAMIENTO DEL TEXTO DEVUELTO POR LA IA
# ------------------------------------------------------

def clean_ai_text(text):
    """
    Elimina residuos de markdown para que los informes se
    vean profesionales en pantalla, PDF y exportaciones.
    Conservativo: solo quita sintaxis, nunca contenido.
    """
    if not text:
        return text

    # negritas y cursivas (**texto**, __texto__)
    text = text.replace("**", "").replace("__", "")

    # titulos markdown al inicio de linea (## Titulo)
    text = re.sub(r"(?m)^#{1,6}\s*", "", text)

    # lineas separadoras (---, ***, ___, ===)
    text = re.sub(r"(?m)^\s*(-{3,}|\*{3,}|_{3,}|={3,})\s*$", "", text)

    # dobles guiones sueltos como separador (-- o -- al final)
    text = re.sub(r"(?m)^\s*--+\s*$", "", text)
    text = re.sub(r"--+(\s*\n)", r"\1", text)

    # backticks de codigo
    text = text.replace("`", "")

    # espacios/tab al final de cada linea
    text = re.sub(r"[ \t]+$", "", text, flags=re.M)

    # lineas que quedaron con solo espacios
    text = re.sub(r"(?m)^[ \t]+$", "", text)

    # colapsar 3 o mas saltos de linea en 2
    text = re.sub(r"\n[ \t]*\n[ \t]*\n+", "\n\n", text)

    return text.strip()
