"""Preflight 2.4B-1: configuración, conexión y revisión de esquema."""
import os
import sys
from sqlalchemy import inspect, text
from alembic.config import Config as AlembicConfig
from alembic.script import ScriptDirectory
from database.session import engine
from config import Config

REQUIRED_TABLES = {
    "users", "schools", "documents", "ai_generations",
    "exports", "usage_events", "alembic_version",
}

print("AulaMind 2.4B-1 staging preflight")
print("Motor:", engine.url.get_backend_name())
print("Destino:", engine.url.render_as_string(hide_password=True))

if os.getenv("STAGING") == "1":
    assert engine.url.get_backend_name() == "postgresql", "STAGING=1 requiere PostgreSQL."
    assert Config.DEBUG is False, "Staging requiere DEBUG=False."
    assert Config.SESSION_COOKIE_SECURE is True, "Staging requiere cookie segura."
    assert Config.RATELIMIT_STORAGE_URI != "memory://", "Staging no puede usar rate limit en memoria."
    assert Config.MAIL_SERVER, "Staging requiere MAIL_SERVER."
    assert Config.MAIL_FROM, "Staging requiere MAIL_FROM."

with engine.connect() as conn:
    conn.execute(text("SELECT 1"))
    tables = set(inspect(conn).get_table_names())
    missing = REQUIRED_TABLES - tables
    if missing:
        print("ERROR: faltan tablas:", ", ".join(sorted(missing)))
        sys.exit(2)

    db_revision = conn.execute(text("SELECT version_num FROM alembic_version")).scalar_one()

cfg = AlembicConfig("alembic.ini")
head = ScriptDirectory.from_config(cfg).get_current_head()
assert db_revision == head, f"Base en {db_revision}; Alembic head es {head}"

print({"database": "OK", "schema": "OK", "alembic_revision": db_revision})
print("STAGING PREFLIGHT OK")
