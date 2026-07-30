"""
===========================================================
AulaMind Enterprise 3.0
scripts/backup_db.py
-----------------------------------------------------------
Respaldo completo de la base de datos a un archivo JSON.

No requiere pg_dump ni herramientas externas: usa SQLAlchemy
directamente. Funciona con PostgreSQL y SQLite.

Uso (PowerShell, apuntando a producción):
    $env:DATABASE_URL="postgresql://...external-url..."
    python scripts/backup_db.py

Uso (local, BD de desarrollo):
    python scripts/backup_db.py

Salida:
    backups/aulamind_backup_YYYYMMDD_HHMMSS.json

Autor:
Biotecno Chile
===========================================================
"""

import importlib
import json
import os
import pkgutil
import sys
from datetime import date, datetime
from decimal import Decimal

# ----------------------------------------------------------
# Raíz del proyecto
# ----------------------------------------------------------

ROOT = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

sys.path.insert(0, ROOT)
os.chdir(ROOT)

import models

for module in pkgutil.iter_modules(models.__path__):
    importlib.import_module(f"models.{module.name}")

import sqlalchemy
from database.base import Base
from config import Config


def serialize(value):
    """Convierte valores no-JSON a representación serializable."""

    if isinstance(value, (datetime, date)):
        return {"__type__": "datetime", "value": value.isoformat()}

    if isinstance(value, bytes):
        return {"__type__": "bytes", "value": value.hex()}

    if isinstance(value, Decimal):
        return {"__type__": "decimal", "value": str(value)}

    # Fallback: cualquier tipo desconocido se guarda como
    # texto. Un respaldo NO debe fallar por una columna rara.
    if value is not None and not isinstance(
        value, (str, int, float, bool, list, dict)
    ):
        return {"__type__": "text", "value": str(value)}

    return value


def main():

    uri = Config.SQLALCHEMY_DATABASE_URI

    # No mostrar credenciales en pantalla
    safe_uri = uri.split("@")[-1] if "@" in uri else uri

    print(f"Origen: ...{safe_uri}")

    engine = sqlalchemy.create_engine(uri)

    metadata = Base.metadata

    backup = {
        "app": "AulaMind Enterprise 3.0",
        "created_at": datetime.utcnow().isoformat(),
        "tables": {},
    }

    total_rows = 0

    # sorted_tables respeta el orden de dependencias FK
    for table in metadata.sorted_tables:

        with engine.connect() as conn:

            rows = conn.execute(
                sqlalchemy.select(table)
            ).mappings().all()

        data = []

        for row in rows:

            data.append({
                key: serialize(value)
                for key, value in dict(row).items()
            })

        backup["tables"][table.name] = data

        total_rows += len(data)

        print(f"  {table.name}: {len(data)} filas")

    # ------------------------------------------------------
    # Guardar
    # ------------------------------------------------------

    os.makedirs("backups", exist_ok=True)

    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    filename = f"backups/aulamind_backup_{stamp}.json"

    with open(filename, "w", encoding="utf-8") as f:
        json.dump(backup, f, ensure_ascii=False, indent=1)

    size_kb = os.path.getsize(filename) // 1024

    print()
    print(f"[OK] Respaldo completo: {filename}")
    print(f"     {len(backup['tables'])} tablas, "
          f"{total_rows} filas, {size_kb} KB")
    print()
    print("Guárdalo en un lugar seguro (Drive, USB).")
    print("Para restaurar: python scripts/restore_db.py "
          + filename)


if __name__ == "__main__":
    main()
