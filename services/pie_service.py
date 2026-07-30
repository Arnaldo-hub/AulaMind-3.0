"""
===========================================================
AulaMind Enterprise 3.0
services/pie_service.py
-----------------------------------------------------------
Motor de Adecuaciones Curriculares PIE IA
===========================================================
"""

from services.openai_service import OpenAIService


class PIEService:

    def __init__(self):
        self.ai = OpenAIService()

    def _system_prompt(self):
        return """
Eres AulaMind IA, un experto en educación inclusiva, PIE (Programa de Integración Escolar) y adecuaciones curriculares del MINEDUC de Chile.

Tu trabajo es crear ADECUACIONES CURRICULARES de alta calidad para docentes, diseñadas para estudiantes con Necesidades Educativas Especiales (NEE).

La adecuación debe ser:
- Alineada al currículum nacional chileno
- Basada en el diagnóstico del estudiante
- Con objetivos adaptados medibles
- Con estrategias diferenciadas concretas
- Con recursos y apoyos específicos
- Con indicadores de evaluación adaptados

ESTRUCTURA OBLIGATORIA (usa exactamente estos títulos):

═══════════════════════════════════════
ADECUACIÓN CURRICULAR PIE
═══════════════════════════════════════

📋 1. IDENTIFICACIÓN DEL ESTUDIANTE
   • Nombre: _______________
   • Curso: _______________
   • Asignatura: _______________
   • Unidad: _______________
   • OA: _______________
   • Fecha: _______________

🏥 2. DIAGNÓSTICO Y CARACTERIZACIÓN
   • Tipo de NEE: _______________
   • Descripción del diagnóstico: _______________
   • Fortalezas del estudiante: _______________
   • Dificultades identificadas: _______________

🎯 3. OBJETIVOS DE APRENDIZAJE ADAPTADOS
   (Mínimo 2 objetivos adaptados al nivel del estudiante, redactados en infinitivo)

🛠️ 4. ESTRATEGIAS DIFERENCIADAS
   • Estrategias de enseñanza: _______________
   • Estrategias de aprendizaje: _______________
   • Adaptaciones de contenido: _______________
   • Adaptaciones de proceso: _______________
   • Adaptaciones de producto: _______________

📚 5. RECURSOS Y APOYOS
   • Material concreto: _______________
   • Tecnología asistiva: _______________
   • Apoyos humanos: _______________
   • Ajustes de tiempo: _______________

📊 6. INDICADORES DE EVALUACIÓN ADAPTADOS
   (Criterios observables y medibles para evaluar el progreso del estudiante)

💡 7. SUGERENCIAS PARA EL DOCENTE
   (Recomendaciones prácticas para implementar la adecuación en el aula)

═══════════════════════════════════════

REGLAS:
- No uses emojis decorativos, solo los indicados en los títulos de sección.
- Usa lenguaje claro, académico y respetuoso.
- Adapta el nivel de complejidad al diagnóstico del estudiante.
- Incluye ejemplos concretos en las estrategias.
"""

    def _user_prompt(self, data):
        return f"""
Genera una adecuación curricular PIE con la siguiente información:

Asignatura: {data.get("asignatura", "No especificada")}
Curso: {data.get("curso", "No especificado")}
Unidad: {data.get("unidad", "No especificada")}
Objetivo de Aprendizaje (OA): {data.get("objetivo", "No especificado")}
Tema: {data.get("tema", "No especificado")}

Diagnóstico del estudiante:
• Tipo de NEE: {data.get("nee", "No especificado")}
• Nivel de adecuación: {data.get("nivel_adecuacion", "Significativa")}
• Descripción del diagnóstico: {data.get("diagnostico", "No especificado")}
• Fortalezas: {data.get("fortalezas", "No especificadas")}
• Dificultades: {data.get("dificultades", "No especificadas")}

Instrucciones:
- Adapta los objetivos al nivel de adecuación indicado.
- Las estrategias deben ser concretas y aplicables en el aula.
- Incluye recursos realistas para el contexto escolar chileno.
- Los indicadores deben ser observables y medibles.

Genera la adecuación completa ahora.
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
            "content": "ADECUACIÓN CURRICULAR PIE\n\n📋 1. IDENTIFICACIÓN\n• Nombre: Juan Pérez\n• Curso: 3° Básico\n• Asignatura: Lenguaje\n...\n\n🏥 2. DIAGNÓSTICO\n• Tipo de NEE: TDAH\n• Descripción: Dificultad para mantener atención sostenida...\n..."
        }