"""
===========================================================
AulaMind Enterprise 3.0
scripts/restore_db.py
-----------------------------------------------------------
Restaura un respaldo JSON (creado por backup_db.py) en la
base de datos configurada por DATABASE_URL.

⚠️  DESTRUCTIVO: vacía las tablas antes de insertar.
    Usar solo sobre una base de datos NUEVA y vacía,
    o sabiendo que se reemplazará todo el contenido.

Uso (PowerShell):
    $env:DATABASE_URL="postgresql://...nueva-bd..."
    python scripts/restore_db.py backups/aulamind_backup_XXXX.json

Autor:
Biotecno Chile
===========================================================
"""

import importlib
import json
import os
import pkgutil
import sys
from datetime import datetime

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


def deserialize(value):
    """Revierte la serialización de backup_db.py."""

    if isinstance(value, dict) and "__type__" in value:

        if value["__type__"] == "datetime":
            return datetime.fromisoformat(value["value"])

        if value["__type__"] == "bytes":
            return bytes.fromhex(value["value"])

    return value


def main():

    if len(sys.argv) < 2:
        print("Uso: python scripts/restore_db.py "
              "backups/archivo.json")
        sys.exit(1)

    backup_file = sys.argv[1]

    if not os.path.exists(backup_file):
        print(f"[ERROR] No existe el archivo: {backup_file}")
        sys.exit(1)

    with open(backup_file, encoding="utf-8") as f:
        backup = json.load(f)

    print(f"Respaldo: {backup_file}")
    print(f"Creado:   {backup.get('created_at')}")
    print(f"Tablas:   {len(backup.get('tables', {}))}")
    print()

    uri = Config.SQLALCHEMY_DATABASE_URI

    safe_uri = uri.split("@")[-1] if "@" in uri else uri

    print(f"Destino: ...{safe_uri}")
    print()
    print("⚠️  ESTO VACÍA LAS TABLAS DEL DESTINO "
          "Y LAS REEMPLAZA CON EL RESPALDO.")
    confirm = input("Escribe SI para continuar: ")

    if confirm.strip().upper() != "SI":
        print("Operación cancelada.")
        sys.exit(0)

    engine = sqlalchemy.create_engine(uri)

    metadata = Base.metadata

    # Crear esquema si no existe
    metadata.create_all(engine)

    tables_in_backup = backup["tables"]

    total_rows = 0

    with engine.begin() as conn:

        # --------------------------------------------------
        # 1. Vaciar en orden inverso (hijos antes que padres)
        # --------------------------------------------------

        for table in reversed(metadata.sorted_tables):

            if table.name in tables_in_backup:
                conn.execute(table.delete())

        # --------------------------------------------------
        # 2. Insertar en orden de dependencias
        # --------------------------------------------------

        for table in metadata.sorted_tables:

            rows = tables_in_backup.get(table.name)

            if not rows:
                continue

            data = [
                {
                    key: deserialize(value)
                    for key, value in row.items()
                }
                for row in rows
            ]

            conn.execute(table.insert(), data)

            total_rows += len(data)

            print(f"  {table.name}: {len(data)} filas")

    print()
    print(f"[OK] Restauración completa: {total_rows} filas")


if __name__ == "__main__":
    main()
