"""
===========================================================
AulaMind Enterprise 3.0
scripts/clean_historic_markdown.py
-----------------------------------------------------------

Migracion v3.7.1 - Limpieza de markdown en documentos
generados antes del formato profesional global.

Requisito: v3.7 desplegada (services/format_rules.py).

Que hace:
  - Revisa TODOS los documentos guardados (tabla documents)
  - Detecta residuos de markdown: **, ##, __, backticks, ---
  - Aplica clean_ai_text() SOLO donde hay cambios
  - Idempotente: correrlo 2 veces es seguro (2da vez = 0 cambios)

Uso (dry-run primero, siempre):
  python scripts/clean_historic_markdown.py            # solo reporta
  python scripts/clean_historic_markdown.py --apply    # aplica cambios

Donde correrlo:
  Opcion A (recomendada): Render Dashboard -> tu servicio ->
           Shell -> python scripts/clean_historic_markdown.py
           (la Shell ya tiene DATABASE_URL de produccion)
  Opcion B: local, con la External Database URL de Render
           exportada como DATABASE_URL en tu .env

Autor:
Biotecno Chile
===========================================================
"""

import argparse
import os
import sys

# Permite correrlo desde cualquier directorio
sys.path.insert(
    0,
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)

from dotenv import load_dotenv
load_dotenv()

# TODOS los modelos deben importarse para que SQLAlchemy
# registre el metadata completo (las FK de Document apuntan
# a users/schools; sin esto el flush falla). Mismo patron
# que app.py.
from models.user import User  # noqa: F401
from models.school import School  # noqa: F401
from models.subscription import Subscription  # noqa: F401
from models.course import Course  # noqa: F401
from models.subject import Subject  # noqa: F401
from models.unit import Unit  # noqa: F401
from models.learning_objective import LearningObjective  # noqa: F401
from models.document import Document
from models.ai_generation import AIGeneration  # noqa: F401
from models.export import Export  # noqa: F401
from models.usage_event import UsageEvent  # noqa: F401
from models.user_subscription import UserSubscription  # noqa: F401
from models.school_subscription import SchoolSubscription  # noqa: F401

from database.session import SessionLocal
from services.format_rules import clean_ai_text


# ------------------------------------------------------
# DETECCION DE RESIDUOS
# ------------------------------------------------------

def has_markdown_residue(text):
    """True si el texto contiene sintaxis markdown tipica."""
    if not text:
        return False

    if "**" in text or "__" in text or "```" in text:
        return True

    for line in text.splitlines():
        s = line.strip()
        # titulos markdown
        if s.startswith("#"):
            return True
        # separadores horizontales
        if s in ("---", "***", "___", "==="):
            return True
        # doble guion al final de linea (separador frecuente)
        if s.endswith("--"):
            return True
        # backtick suelto
        if "`" in s:
            return True

    return False


# ------------------------------------------------------
# MIGRACION
# ------------------------------------------------------

def run(apply_changes=False):
    db = SessionLocal()
    try:
        total = 0
        afectados = 0
        por_tipo = {}
        muestra = None

        query = db.query(Document).order_by(Document.created_at)

        for doc in query.yield_per(200):
            total += 1
            content = doc.content or ""

            if not has_markdown_residue(content):
                continue

            cleaned = clean_ai_text(content)

            if cleaned == content.strip():
                continue

            afectados += 1
            tipo = doc.document_type or "sin_tipo"
            por_tipo[tipo] = por_tipo.get(tipo, 0) + 1

            if muestra is None:
                muestra = (doc.id, doc.title, content[:400], cleaned[:400])

            if apply_changes:
                doc.content = cleaned
                doc.version = (doc.version or 1) + 1

            if apply_changes and afectados % 200 == 0:
                db.commit()

        if apply_changes:
            db.commit()

        print("=" * 60)
        print("MIGRACION FORMATO PROFESIONAL v3.7.1")
        print("=" * 60)
        print(f"Documentos revisados : {total}")
        print(f"Con residuo markdown : {afectados}")
        print(f"Modo                 : {'APLICADO' if apply_changes else 'DRY-RUN (sin cambios)'}")
        print("-" * 60)
        if por_tipo:
            print("Afectados por tipo:")
            for tipo, n in sorted(por_tipo.items()):
                print(f"  - {tipo}: {n}")
        else:
            print("Nada que limpiar. Todo el contenido ya esta limpio.")

        if muestra:
            print("-" * 60)
            print("MUESTRA (primer documento afectado):")
            print(f"  id    : {muestra[0]}")
            print(f"  titulo: {muestra[1]}")
            print("  ANTES :")
            print("    " + muestra[2].replace("\n", "\n    "))
            print("  DESPUES:")
            print("    " + muestra[3].replace("\n", "\n    "))
        print("=" * 60)

    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Limpia markdown historico de documents"
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Aplica los cambios (sin este flag solo reporta)",
    )
    args = parser.parse_args()

    if not os.getenv("DATABASE_URL"):
        print("ERROR: DATABASE_URL no configurada.")
        print("Correlo en la Shell de Render o exporta la")
        print("External Database URL de tu BD como DATABASE_URL.")
        sys.exit(1)

    run(apply_changes=args.apply)
