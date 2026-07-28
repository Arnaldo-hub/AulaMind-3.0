""" 
AulaMind Enterprise 3.0
services/guide_service.py
-----------------------------------------------------------
Motor de Guías de Apoyo y Aprendizaje IA
Autor: Biotecno Chile
""" 

from services.openai_service import OpenAIService


class GuideService:
    def __init__(self):
        self.ai = OpenAIService()

    def _system_prompt(self):
        return """
Eres AulaMind IA, un experto en pedagogía, didáctica y currículum nacional de Chile.
Tu trabajo es crear guías de apoyo y material complementario para docentes.
La guía debe contener SIEMPRE:
1. Título claro y alineado al OA
2. Objetivo de la guía
3. Conceptos clave
4. Ejemplos resueltos paso a paso
5. Ejercicios de práctica
6. Autoevaluación o checklist
7. Criterios de logro / Indicadores de evaluación
No escribas explicaciones adicionales. Devuelve solamente la guía completa.
"""

    def _user_prompt(self, data):
        return f"""
Genera una guía de apoyo con la siguiente información:
Asignatura: {data.get("asignatura")}
Curso: {data.get("curso")}
Unidad: {data.get("unidad")}
Objetivo de Aprendizaje: {data.get("objetivo")}
Tema: {data.get("tema")}
Tipo de guía: {data.get("tipo")}
Nivel de dificultad: {data.get("dificultad")}
La guía debe incluir resumen teórico, ejemplos resueltos, ejercicios, autoevaluación e indicadores.
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
            "content": "GUÍA DE APOYO: FRACCIONES EQUIVALENTES\nCurso: 5° Básico\nUnidad: Fracciones\nOA: OA11\n..."
        }
