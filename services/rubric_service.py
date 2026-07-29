"""
===========================================================
AulaMind Enterprise 3.0
services/rubric_service.py
-----------------------------------------------------------
Motor de Rúbricas y Listas de Cotejo IA
===========================================================
"""

from services.openai_service import OpenAIService


class RubricService:

    def __init__(self):
        self.ai = OpenAIService()

    def _system_prompt(self):
        return """
Eres AulaMind IA, un experto en evaluación educativa, pedagogía y currículum nacional del MINEDUC de Chile.

Tu trabajo es crear RÚBRICAS ANALÍTICAS y LISTAS DE COTEJO de alta calidad para docentes. Las rúbricas deben ser:
- Alineadas al currículum nacional chileno
- Con criterios observables y medibles
- Con descriptores claros para cada nivel de desempeño
- Listas para imprimir o proyectar en el aula

ESTRUCTURA OBLIGATORIA (usa exactamente estos títulos):

═══════════════════════════════════════
RÚBRICA: [Tema]
═══════════════════════════════════════

📋 1. IDENTIFICACIÓN
   • Asignatura:
   • Curso:
   • Unidad:
   • OA (Objetivo de Aprendizaje):
   • Tema:
   • Tipo de rúbrica:
   • Puntaje máximo:

🎯 2. OBJETIVO DE LA EVALUACIÓN
   (Redacta qué se evaluará y para qué)

📊 3. RÚBRICA ANALÍTICA

| CRITERIO | Excelente (4) | Logrado (3) | En desarrollo (2) | Inicial (1) | Puntaje |
|----------|---------------|-------------|-------------------|-------------|---------|
| [Criterio 1] | [Descriptor] | [Descriptor] | [Descriptor] | [Descriptor] | ___/4 |
| [Criterio 2] | [Descriptor] | [Descriptor] | [Descriptor] | [Descriptor] | ___/4 |
| ... | ... | ... | ... | ... | ... |

📋 4. INSTRUCCIONES DE USO PARA EL DOCENTE
   (Cómo aplicar la rúbrica, cuándo, en qué contexto)

💡 5. SUGERENCIAS DE RETROALIMENTACIÓN
   (Frases modelo para cada nivel de desempeño)

═══════════════════════════════════════

REGLAS:
- No uses emojis decorativos, solo los indicados en los títulos.
- Los descriptores deben ser observables y medibles.
- Adapta los criterios al nivel de dificultad solicitado.
- Incluye un encabezado ficticio: "Nombre: _______________ | Fecha: _______________"
"""

    def _user_prompt(self, data):
        return f"""
Genera una rúbrica analítica con los siguientes datos:

Asignatura: {data.get("asignatura", "No especificada")}
Curso: {data.get("curso", "No especificado")}
Unidad: {data.get("unidad", "No especificada")}
Objetivo de Aprendizaje (OA): {data.get("objetivo", "No especificado")}
Tema: {data.get("tema", "No especificado")}
Tipo de rúbrica: {data.get("tipo", "Analítica")}
Nivel de dificultad: {data.get("dificultad", "Intermedia")}
Criterios a evaluar: {data.get("criterios", "Generar criterios apropiados")}

Instrucciones:
- Si el tipo es "Analítica": tabla con 4 niveles (Excelente, Logrado, En desarrollo, Inicial).
- Si el tipo es "Lista de cotejo": lista de ítems con casillas de verificación.
- Si el tipo es "Holística": descripción general por nivel sin criterios separados.
- Adapta los descriptores al nivel de dificultad.

Genera la rúbrica completa ahora.
"""

    def generate(self, data):
        try:
            resultado = self.ai.generate(self._system_prompt(), self._user_prompt(data))
            if not resultado.get("success"):
                return resultado
            return {"success": True, "content": resultado.get("content")}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def preview(self, texto):
        return {"success": True, "preview": texto}

    def sample(self):
        return {
            "success": True,
            "content": "RÚBRICA: Expresión Oral\n\n📋 1. IDENTIFICACIÓN\n• Asignatura: Lenguaje\n• Curso: 4° Básico\n...\n\n📊 3. RÚBRICA ANALÍTICA\n| CRITERIO | Excelente | Logrado | En desarrollo | Inicial |\n|----------|-----------|---------|---------------|---------|\n| Claridad | Se expresa con fluidez | Se expresa con claridad | Se expresa con dificultad | No se logra comunicar |\n..."
        }