"""
===========================================================
AulaMind Enterprise 3.0
services/guide_service.py
-----------------------------------------------------------
Motor de Guías de Apoyo y Aprendizaje IA
Prompt optimizado para docentes chilenos — MINEDUC
===========================================================
"""

from services.openai_service import OpenAIService


class GuideService:

    def __init__(self):
        self.ai = OpenAIService()

    # ======================================================
    # PROMPT DEL SISTEMA — GUÍA PROFESIONAL
    # ======================================================

    def _system_prompt(self):
        return """
Eres AulaMind IA, un experto en pedagogía, didáctica y currículum nacional del MINEDUC de Chile.

Tu trabajo es crear GUÍAS DE APOYO PEDAGÓGICO de alta calidad para docentes. Las guías deben ser:
- Listas para imprimir o proyectar en el aula
- Alineadas al currículum nacional chileno
- Con lenguaje claro, académico y motivador
- Con actividades diferenciadas según nivel de dificultad

ESTRUCTURA OBLIGATORIA (usa exactamente estos títulos):

═══════════════════════════════════════
GUÍA DE APOYO: [Tema]
═══════════════════════════════════════

📋 1. IDENTIFICACIÓN
   • Asignatura:
   • Curso:
   • Unidad:
   • OA (Objetivo de Aprendizaje):
   • Tema:
   • Tiempo estimado:
   • Nivel de dificultad:

🎯 2. OBJETIVO DE LA GUÍA
   (Redacta en infinitivo qué aprenderá el estudiante al finalizar)

📚 3. CONCEPTOS CLAVE
   (Máximo 5 conceptos con definición breve y clara)

✏️ 4. EJEMPLOS RESUELTOS
   (Mínimo 2 ejemplos paso a paso con explicación didáctica)

📝 5. EJERCICIOS DE PRÁCTICA
   (Mínimo 5 ejercicios variados: selección múltiple, verdadero/falso, desarrollo)
   (Incluye espacio con líneas punteadas para que el estudiante escriba)

✅ 6. AUTOEVALUACIÓN DEL ESTUDIANTE
   (Checklist de 4 a 6 ítems que el estudiante marca con ✓ o ✗)

📊 7. INDICADORES DE EVALUACIÓN ALINEADOS AL OA
   (Lista de criterios observables para el docente)

💡 8. SUGERENCIAS DIDÁCTICAS PARA EL DOCENTE
   (Estrategias de aula, recursos recomendados, adaptaciones PIE si aplica)

═══════════════════════════════════════

REGLAS:
- No uses emojis decorativos, solo los indicados en los títulos de sección.
- Usa formato limpio con líneas separadoras.
- Las respuestas de los ejercicios van al final en una sección "SOLUCIONARIO".
- Adapta el contenido al nivel de dificultad solicitado (Básica/Intermedia/Avanzada).
- Incluye un encabezado ficticio tipo: "Colegio _______________ | Nombre: _______________ | Fecha: _______________"
"""

    # ======================================================
    # PROMPT DEL USUARIO
    # ======================================================

    def _user_prompt(self, data):
        return f"""
Genera una guía de apoyo pedagógica con los siguientes datos:

Asignatura: {data.get("asignatura", "No especificada")}
Curso: {data.get("curso", "No especificado")}
Unidad: {data.get("unidad", "No especificada")}
Objetivo de Aprendizaje (OA): {data.get("objetivo", "No especificado")}
Tema: {data.get("tema", "No especificado")}
Tipo de guía: {data.get("tipo", "Ficha de trabajo")}
Nivel de dificultad: {data.get("dificultad", "Intermedia")}

Instrucciones adicionales:
- Si el nivel es BÁSICA: ejercicios guiados, mucho scaffolding, vocabulario simplificado.
- Si el nivel es INTERMEDIA: ejercicios mixtos, algunos desafíos.
- Si el nivel es AVANZADA: ejercicios de mayor complejidad, análisis y aplicación.

Genera la guía completa ahora.
"""

    # ======================================================
    # GENERAR
    # ======================================================

    def generate(self, data):
        try:
            resultado = self.ai.generate(
                self._system_prompt(),
                self._user_prompt(data)
            )
            if not resultado.get("success"):
                return resultado
            return {
                "success": True,
                "content": resultado.get("content")
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    # ======================================================
    # PREVIEW
    # ======================================================

    def preview(self, texto):
        return {
            "success": True,
            "preview": texto
        }

    # ======================================================
    # EJEMPLO
    # ======================================================

    def sample(self):
        return {
            "success": True,
            "content": """
═══════════════════════════════════════
GUÍA DE APOYO: Fracciones Equivalentes
═══════════════════════════════════════

Colegio _______________ | Nombre: _______________ | Fecha: _______________

📋 1. IDENTIFICACIÓN
   • Asignatura: Matemática
   • Curso: 5° Básico
   • Unidad: Números y Operaciones
   • OA: OA11 — Identificar y representar fracciones equivalentes
   • Tema: Fracciones equivalentes
   • Tiempo estimado: 45 minutos
   • Nivel de dificultad: Intermedia

🎯 2. OBJETIVO DE LA GUÍA
   Comprender el concepto de fracciones equivalentes, identificarlas en representaciones gráficas y numéricas, y aplicar amplificación y simplificación.

📚 3. CONCEPTOS CLAVE
   • Fracción: Representación de una parte de un todo.
   • Fracciones equivalentes: Aquellas que representan la misma cantidad aunque tengan numerador y denominador diferentes.
   • Amplificación: Multiplicar numerador y denominador por el mismo número.
   • Simplificación: Dividir numerador y denominador por el mismo número.

✏️ 4. EJEMPLOS RESUELTOS

Ejemplo 1: ¿Son equivalentes 1/2 y 2/4?
   Paso 1: Multiplicamos 1 × 2 = 2 y 2 × 2 = 4.
   Paso 2: Obtenemos 2/4, que es igual a 1/2.
   Respuesta: Sí son equivalentes.

Ejemplo 2: Simplifica 6/9 al máximo.
   Paso 1: Buscamos un divisor común de 6 y 9. El 3 divide a ambos.
   Paso 2: 6 ÷ 3 = 2; 9 ÷ 3 = 3.
   Respuesta: 2/3

📝 5. EJERCICIOS DE PRÁCTICA

1) Encierra en un círculo las fracciones equivalentes a 3/4:
   a) 6/8    b) 9/12    c) 5/8    d) 12/16
   Respuesta: ............................

2) Escribe tres fracciones equivalentes a 2/5 usando amplificación.
   ............................................................
   ............................................................
   ............................................................

3) Verdadero o Falso: "Dos fracciones equivalentes siempre tienen el mismo denominador."
   Respuesta: ............................

4) Representa gráficamente (en una recta numérica) las fracciones 1/2, 2/4 y 3/6.
   ............................................................

5) Resuelve: Marta tiene 3/4 de una pizza y Pedro tiene 6/8. ¿Tienen la misma cantidad? Justifica.
   ............................................................
   ............................................................

✅ 6. AUTOEVALUACIÓN DEL ESTUDIANTE

   □ Puedo explicar con mis palabras qué son fracciones equivalentes.
   □ Puedo encontrar fracciones equivalentes usando amplificación.
   □ Puedo simplificar una fracción al máximo.
   □ Puedo representar fracciones equivalentes gráficamente.
   □ Puedo resolver problemas que involucren fracciones equivalentes.

📊 7. INDICADORES DE EVALUACIÓN ALINEADOS AL OA

   • Identifica fracciones equivalentes en representaciones concretas, pictóricas y simbólicas.
   • Aplica procedimientos de amplificación y simplificación correctamente.
   • Resuelve problemas contextualizados usando fracciones equivalentes.
   • Justifica sus respuestas con argumentos matemáticos.

💡 8. SUGERENCIAS DIDÁCTICAS PARA EL DOCENTE

   • Recursos: Papel milimetrado, fraccionarios de plástico, recta numérica gigante.
   • Estrategia: Trabajo en parejas con "explicador" y "verificador".
   • Adaptación PIE: Para estudiantes con dificultades, usar material concreto (pizzas de fracciones).
   • Extensión: Desafío avanzado — encontrar la fracción equivalente con el menor denominador posible.

═══════════════════════════════════════
SOLUCIONARIO
═══════════════════════════════════════

1) a) 6/8, b) 9/12, d) 12/16
2) 4/10, 6/15, 8/20 (u otras válidas)
3) Falso. Pueden tener denominadores diferentes.
4) [Representación gráfica: tres marcas en el mismo punto de la recta]
5) Sí. 3/4 = 6/8 porque 3×2=6 y 4×2=8.
"""
        }