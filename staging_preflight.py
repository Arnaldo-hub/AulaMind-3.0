"""Preflight seguro para SQLite local y PostgreSQL staging."""
import os, sys
from sqlalchemy import inspect, text
from database.session import engine

REQUIRED = {"users","schools","documents","ai_generations","exports","usage_events"}
url = engine.url
print("AulaMind staging preflight")
print("Motor:", url.get_backend_name())
print("Destino:", url.render_as_string(hide_password=True))
if url.get_backend_name() == "sqlite" and os.getenv("STAGING") == "1":
    raise SystemExit("ERROR: STAGING=1 no puede usar SQLite.")
with engine.connect() as conn:
    conn.execute(text("SELECT 1"))
    tables = set(inspect(conn).get_table_names())
missing = REQUIRED - tables
if missing:
    print("ERROR: faltan tablas:", ", ".join(sorted(missing)))
    sys.exit(2)
print("Conexión OK. Esquema mínimo SaaS OK.")
