"""
===========================================================
AulaMind Enterprise 3.0
services/tools_service.py
-----------------------------------------------------------

Herramientas IA de Apoyo (v3.5)

Asistente de texto libre + plantillas para asistentes
de la educación: cuentos, textos, ideas de actividades
y apoyo administrativo. Reutiliza OpenAIService.

Fase 2 (imágenes) queda preparada pero apagada hasta
decisión de producto (costos por imagen).

Autor:
Biotecno Chile
===========================================================
"""

import logging
import os

from services.openai_service import OpenAIService

logger = logging.getLogger(__name__)


# ==========================================================
# Reglas de formato profesional (v3.5.1)
# Aplicadas a TODAS las plantillas. Evitan cierres con
# preguntas, markdown crudo y links de imágenes falsos.
# ==========================================================

OUTPUT_RULES = (
    "\n\nREGLAS DE FORMATO Y ENTREGA (obligatorias):"
    "\n- Entrega SOLO lo solicitado, completo y terminado."
    "\n- NO agregues preguntas al final ni ofertas de ayuda adicional."
    "\n- NO preguntes si desea ajustes, otra version o algo mas."
    "\n- NO uses sintaxis markdown (sin ##, **, --- ni viñetas con asterisco)."
    "\n- Usa texto plano estructurado: titulos en MAYUSCULAS y lineas en blanco entre secciones."
    "\n- NO incluyas enlaces ni imagenes; no puedes generar imagenes, no las menciones."
    "\n- Cierra con el contenido final, sin despedidas ni cierres conversacionales."
)


class ToolsService:
    """
    Motor de las Herramientas IA de apoyo.
    """

    # -------------------------------------------------
    # Plantillas de system prompt por tipo de tarea
    # -------------------------------------------------

    TEMPLATES = {
        "libre": {
            "name": "Asistente Libre",
            "icon": "fa-comments",
            "description": "Conversa con la IA sobre cualquier tema de tu trabajo.",
            "system": (
                "Eres AulaMind, un asistente experto en educación chilena. "
                "Ayudas a asistentes de la educación, docentes y equipos "
                "directivos con sus tareas diarias: redacción, ideas, "
                "resolución de dudas y apoyo pedagógico. "
                "Respondes en español, de forma clara, práctica y lista "
                "para usar. Usa viñetas y estructura cuando ayude."
            ),
            "placeholder": "Escribe tu consulta o texto aquí...",
        },
        "cuento": {
            "name": "Crear un Cuento",
            "icon": "fa-book-open",
            "description": "Genera un cuento infantil con personajes, inicio, desarrollo y cierre.",
            "system": (
                "Eres un escritor de literatura infantil experto. "
                "Creas cuentos originales en español para niños y niñas "
                "chilenos, con lenguaje adecuado a la edad indicada, "
                "valores positivos y estructura completa (título, "
                "personajes, inicio, desarrollo, cierre y moraleja). "
                "El cuento debe ser encantador, coherente y listo para "
                "leer en voz alta."
            ),
            "placeholder": (
                "Ej: Crea un cuento sobre una niña que cuida el mar, "
                "para niños de 6 años, con un perro juguetón."
            ),
        },
        "texto": {
            "name": "Redactar Texto",
            "icon": "fa-pen-nib",
            "description": "Comunicados, cartas, informes o textos formales.",
            "system": (
                "Eres un redactor profesional del ámbito educacional "
                "chileno. Redactas textos claros, correctos y con tono "
                "adecuado: comunicados a apoderados, cartas, informes, "
                "actas o mensajes institucionales. Pide los datos que "
                "falten si son indispensables; si no, redacta con "
                "supuestos razonables y márcalos entre corchetes."
            ),
            "placeholder": (
                "Ej: Redacta un comunicado a los apoderados sobre la "
                "salida pedagógica del próximo viernes al museo."
            ),
        },
        "actividades": {
            "name": "Ideas de Actividades",
            "icon": "fa-lightbulb",
            "description": "Actividades lúdicas, recreativas y de apoyo para el aula.",
            "system": (
                "Eres una educadora experta en actividades para salas "
                "de educación parvularia y básica en Chile. Propones "
                "actividades concretas, lúdicas y factibles para "
                "asistentes de la educación: materiales, pasos, tiempos "
                "y qué aprendizaje apoyan. Sé práctica y específica."
            ),
            "placeholder": (
                "Ej: Dame 5 actividades para trabajar los colores con "
                "niños de 4 años usando materiales del aula."
            ),
        },
        "apoyo": {
            "name": "Apoyo y Organización",
            "icon": "fa-clipboard-check",
            "description": "Listas, planificación de tareas y apoyo administrativo.",
            "system": (
                "Eres un asistente de organización para equipos "
                "educacionales. Ayudas a crear listas de verificación, "
                "planificar rutinas, organizar materiales, preparar "
                "apoyos visuales y ordenar tareas administrativas "
                "sencillas. Respuestas en formato listo para imprimir."
            ),
            "placeholder": (
                "Ej: Crea una lista de verificación para el cierre "
                "diario del aula de párvulos."
            ),
        },
    }

    # -------------------------------------------------
    # API pública
    # -------------------------------------------------

    def __init__(self):
        self.ai = OpenAIService()

    def list_templates(self):
        return [
            {
                "id": key,
                "name": t["name"],
                "icon": t["icon"],
                "description": t["description"],
                "placeholder": t["placeholder"],
            }
            for key, t in self.TEMPLATES.items()
        ]

    def is_valid_template(self, template_id):
        return template_id in self.TEMPLATES

    def generate(self, template_id, message):
        """
        Genera la respuesta de la IA. Devuelve el dict estándar
        {"success": True, "content": ...} o {"success": False, ...}.
        """
        if not self.is_valid_template(template_id):
            return {
                "success": False,
                "error": f"Plantilla '{template_id}' no válida."
            }

        if not message or not str(message).strip():
            return {
                "success": False,
                "error": "El mensaje no puede estar vacío."
            }

        template = self.TEMPLATES[template_id]

        logger.info(
            "Herramienta IA [%s]: %.80s",
            template_id,
            message
        )

        return self.ai.generate(
            system_prompt=template["system"] + OUTPUT_RULES,
            user_prompt=str(message).strip(),
        )

    def health(self):
        return {
            "service": "ToolsService",
            "version": "3.5",
            "status": "OK",
            "templates": list(self.TEMPLATES.keys()),
            "openai": self.ai.available(),
        }




# ==========================================================
# FASE 2: Generación de imágenes (v3.6)
# Apagada por defecto. Prender en Render con:
#   IMAGES_ENABLED=true
#   IMAGES_DAILY_LIMIT=5          (tope por usuario/día)
#   OPENAI_IMAGE_MODEL=gpt-image-1
# ==========================================================

IMAGES_ENABLED = os.getenv("IMAGES_ENABLED", "false").lower() == "true"
IMAGES_DAILY_LIMIT = int(os.getenv("IMAGES_DAILY_LIMIT", "5"))
OPENAI_IMAGE_MODEL = os.getenv("OPENAI_IMAGE_MODEL", "gpt-image-1")


def generate_image(prompt):
    """
    Genera una imagen con la API de imágenes de OpenAI.
    Devuelve {"success": True, "b64": str} o {"success": False, "error": str}.
    Nunca lanza excepción hacia el route.
    """
    prompt = (prompt or "").strip()

    if not IMAGES_ENABLED:
        return {
            "success": False,
            "error": "La generación de imágenes no está habilitada.",
        }

    if not prompt:
        return {
            "success": False,
            "error": "Describe la imagen que necesitas.",
        }

    if len(prompt) > 1000:
        return {
            "success": False,
            "error": "Descripción demasiado larga (máx. 1000 caracteres).",
        }

    ai = OpenAIService()

    if not ai.available():
        return {
            "success": False,
            "error": "OPENAI_API_KEY no configurada.",
        }

    try:
        response = ai.client.images.generate(
            model=OPENAI_IMAGE_MODEL,
            prompt=(
                "Ilustración profesional, apropiada para educación "
                "infantil y contexto escolar chileno, sin texto ni "
                "marcas de agua: " + prompt
            ),
            size="1024x1024",
        )

        item = response.data[0]

        if getattr(item, "b64_json", None):
            return {"success": True, "b64": item.b64_json}

        if getattr(item, "url", None):
            return {"success": True, "url": item.url}

        return {
            "success": False,
            "error": "La IA no devolvió la imagen. Intenta de nuevo.",
        }

    except Exception as e:
        logger.exception("[tools] error generando imagen")
        return {
            "success": False,
            "error": f"No se pudo generar la imagen: {e}",
        }

# Singleton de proceso
tools_service = ToolsService()

__all__ = ["ToolsService", "tools_service"]
