"""
Bootstrap controlado de persistencia AulaMind.
Uso:
    python manage_db.py bootstrap
    python manage_db.py info
"""
import sys
from sqlalchemy import inspect
from database.session import engine, create_database

# Registrar todos los modelos en metadata.
from models.user import User
from models.school import School
from models.subscription import Subscription
from models.course import Course
from models.subject import Subject
from models.unit import Unit
from models.learning_objective import LearningObjective
from models.document import Document
from models.ai_generation import AIGeneration
from models.export import Export
from models.usage_event import UsageEvent

def info():
    tables = inspect(engine).get_table_names()
    print("DATABASE:", engine.url.render_as_string(hide_password=True))
    print("TABLES:", ", ".join(sorted(tables)))

def bootstrap():
    # Seguro para la BD local existente: create_all solo crea tablas ausentes.
    create_database()
    print("Schema bootstrap OK.")
    print("Ahora ejecute: alembic stamp 20260708_01")
    info()

if __name__ == "__main__":
    command = sys.argv[1] if len(sys.argv) > 1 else "info"
    if command == "bootstrap":
        bootstrap()
    elif command == "info":
        info()
    else:
        raise SystemExit("Uso: python manage_db.py [bootstrap|info]")
