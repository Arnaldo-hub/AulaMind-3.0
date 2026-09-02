"""
===========================================================
AulaMind Enterprise 3.0
services/fonoaudiologia_service.py
-----------------------------------------------------------
Motor de documentos fonoaudiológicos escolares
===========================================================
"""

from services.openai_service import OpenAIService


class FonoaudiologiaService:
    """
    Genera tres tipos de documentos fonoaudiológicos:
    1. Informe Fonoaudiológico Escolar (evaluación completa)
    2. Plan de Intervención Comunicacional (objetivos SMART)
    3. Consejos Rápidos para el Docente (5 tips aplicables)
    """

    def __init__(self):
        self.ai = OpenAIService()

    # -----------------------------------------------------
    # SYSTEM PROMPTS
    # -----------------------------------------------------

    def _system_prompt_informe(self):
        return """Eres un fonoaudiólogo experto con especialización en el contexto escolar chileno.
Generas informes técnicos para equipos PIE, docentes, apoderados y otros profesionales del área.

REGLAS:
- Usa terminología del área: lenguaje receptivo, lenguaje expresivo, pragmático, fonológico, articulatorio, fluidez, voz, habla.
- Alinea tu redacción al Decreto 83/2015 del MINEDUC sobre NEE y al programa PIE.
- Lenguaje claro para docentes, técnico para colegas.
- Incluye recomendaciones aplicables en aula regular.
- NO inventes datos del paciente; usa placeholders cuando falte información.
- NO uses emojis decorativos. Solo texto plano con formato limpio."""

    def _system_prompt_plan(self):
        return """Eres un fonoaudiólogo especialista en intervención temprana y educacional en Chile.
Diseñas planes de intervención comunicacional con objetivos SMART, estrategias diferenciadas y criterios de evaluación medibles.

REGLAS:
- Objetivos en formato SMART (específicos, medibles, alcanzables, relevantes, temporales).
- Estrategias concretas aplicables en el aula chilena.
- Coordina roles entre fonoaudiólogo, docente y familia.
- NO uses emojis decorativos."""

    def _system_prompt_consejos(self):
        return """Eres fonoaudiólogo escolar. Generas consejos PRÁCTICOS y CORTOS para docentes.
Cada consejo debe ser aplicable "mañana mismo" en el aula.
Máximo 3 líneas por consejo.
NO uses emojis."""

    # -----------------------------------------------------
    # USER PROMPTS
    # -----------------------------------------------------

    def _user_prompt_informe(self, data: dict) -> str:
        return f"""Genera un INFORME FONOAUDIOLÓGICO ESCOLAR con la siguiente información:

• Estudiante: {data.get('nombre', '_________________')}
• Curso: {data.get('curso', '_________________')}
• Edad: {data.get('edad', '_________________')}
• Evaluador: {data.get('evaluador', '_________________')}
• Fecha evaluación: {data.get('fecha', '_________________')}
• Motivo derivación: {data.get('motivo', '_________________')}
• Institución: {data.get('colegio', '_________________')}

Antecedentes relevantes:
{data.get('antecedentes', 'No especificados')}

Instrumentos aplicados:
{data.get('instrumentos', 'No especificados')}

Hallazgos observados (si los hay):
{data.get('hallazgos', 'No especificados')}

ESTRUCTURA OBLIGATORIA (usa exactamente estos títulos):

═══════════════════════════════════════
INFORME FONOAUDIOLÓGICO ESCOLAR
═══════════════════════════════════════

1. IDENTIFICACIÓN
2. MOTIVO DE CONSULTA / DERIVACIÓN
3. ANTECEDENTES RELEVANTES
4. EVALUACIÓN REALIZADA
5. HALLAZGOS
   5.1 Lenguaje Receptivo
   5.2 Lenguaje Expresivo
   5.3 Aspecto Pragmático-Social
   5.4 Habla (Articulación, Fluidez, Voz)
   5.5 Lectoescritura (si aplica)
6. DIAGNÓSTICO FONOAUDIOLÓGICO
7. CONCLUSIONES
8. RECOMENDACIONES PARA EL AULA
9. SUGERENCIAS PARA LA FAMILIA
10. DERIVACIONES COMPLEMENTARIAS (si aplica)
11. FIRMA Y TIMBRE PROFESIONAL (placeholder)

REGLAS DE FORMATO:
- No uses emojis decorativos.
- Lenguaje respetuoso y técnico.
- Adapta el nivel de detalle a la información disponible.
- Si falta un dato, usa placeholder _______________."""

    def _user_prompt_plan(self, data: dict) -> str:
        return f"""Genera un PLAN DE INTERVENCIÓN COMUNICACIONAL para:

• Estudiante: {data.get('nombre', '_________________')}
• Curso: {data.get('curso', '_________________')}
• Diagnóstico: {data.get('diagnostico', '_________________')}
• Nivel de adecuación PIE: {data.get('nivel_pie', 'Significativa')}
• Áreas prioritarias: {data.get('areas', 'Lenguaje expresivo y receptivo')}
• Duración sugerida: {data.get('duracion', 'Semestre')}

ESTRUCTURA OBLIGATORIA:

═══════════════════════════════════════
PLAN DE INTERVENCIÓN COMUNICACIONAL
═══════════════════════════════════════

1. IDENTIFICACIÓN DEL ESTUDIANTE
2. DIAGNÓSTICO RESUMIDO
3. OBJETIVOS DE INTERVENCIÓN
   • Corto plazo (4-8 semanas)
   • Mediano plazo (semestre)
   (Formato SMART: específico, medible, alcanzable, relevante, temporal)
4. ESTRATEGIAS DE INTERVENCIÓN
   • Individuales
   • Grupales
   • En el aula (adaptaciones curriculares)
5. RECURSOS Y MATERIALES
6. CRONOGRAMA SUGERIDO
7. INDICADORES DE EVALUACIÓN
8. ROLES Y RESPONSABILIDADES
   • Fonoaudiólogo
   • Docente
   • Familia
9. CRITERIOS DE ALTA O REEVALUACIÓN
"""

    def _user_prompt_consejos(self, data: dict) -> str:
        return f"""Genera EXACTAMENTE 5 consejos prácticos para el docente de aula regular.

• Estudiante: {data.get('nombre', '______')}
• Diagnóstico: {data.get('diagnostico', '______')}
• Curso: {data.get('curso', '______')}
• Área problemática: {data.get('area', 'Lenguaje')}

REGLAS:
- Cada consejo máximo 3 líneas.
- Deben ser aplicables mañana mismo en clase.
- Incluye ejemplos concretos.
n- Formato: lista numerada 1-5.
- Sin introducción ni conclusión. Solo los 5 consejos."""

    # -----------------------------------------------------
    # GENERADORES PÚBLICOS
    # -----------------------------------------------------

    def generar_informe(self, data: dict) -> dict:
        try:
            return self.ai.generate(
                self._system_prompt_informe(),
                self._user_prompt_informe(data),
            )
        except Exception as e:
            return {"success": False, "error": str(e)}

    def generar_plan_intervencion(self, data: dict) -> dict:
        try:
            return self.ai.generate(
                self._system_prompt_plan(),
                self._user_prompt_plan(data),
            )
        except Exception as e:
            return {"success": False, "error": str(e)}

    def generar_consejos_docente(self, data: dict) -> dict:
        try:
            return self.ai.generate(
                self._system_prompt_consejos(),
                self._user_prompt_consejos(data),
            )
        except Exception as e:
            return {"success": False, "error": str(e)}