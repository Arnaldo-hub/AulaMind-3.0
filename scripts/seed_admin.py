"""
===========================================================
AulaMind Enterprise 3.0
scripts/seed_admin.py
-----------------------------------------------------------
Crea (o promueve) la cuenta administradora inicial.

Idempotente: puede ejecutarse varias veces sin duplicar.

Uso local:
    python scripts/seed_admin.py

Uso en Render (Shell del servicio):
    python scripts/seed_admin.py

Variables de entorno (todas opcionales, con defaults):
    ADMIN_EMAIL       (default: admin@aulamind.cl)
    ADMIN_PASSWORD    (default: se genera una segura y se muestra UNA vez)
    ADMIN_FIRST_NAME  (default: Administrador)
    ADMIN_LAST_NAME   (default: AulaMind)

Autor:
Biotecno Chile
===========================================================
"""

import os
import secrets
import string
import sys

# ----------------------------------------------------------
# Raíz del proyecto
# ----------------------------------------------------------

ROOT = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

sys.path.insert(0, ROOT)
os.chdir(ROOT)

import importlib
import pkgutil

import models

# Registrar TODOS los modelos: User tiene relaciones
# con School y Subscription que deben resolverse.
for module in pkgutil.iter_modules(models.__path__):
    importlib.import_module(f"models.{module.name}")

from database.session import SessionLocal
from models.user import User
from services.auth_service import AuthService


def generate_password(length=16):
    """Genera una contraseña que cumple la política del sistema."""

    alphabet = string.ascii_letters + string.digits

    while True:

        password = "".join(
            secrets.choice(alphabet) for _ in range(length)
        )

        try:
            AuthService.validate_password(password)
            return password
        except ValueError:
            continue


def main():

    email = os.getenv(
        "ADMIN_EMAIL", "admin@aulamind.cl"
    ).strip().lower()

    first_name = os.getenv(
        "ADMIN_FIRST_NAME", "Administrador"
    )

    last_name = os.getenv(
        "ADMIN_LAST_NAME", "AulaMind"
    )

    password = os.getenv("ADMIN_PASSWORD", "")
    generated = False

    if not password:
        password = generate_password()
        generated = True

    password_created = False

    db = SessionLocal()

    try:

        user = AuthService.get_user_by_email(db, email)

        if user is None:

            user = User(
                first_name=first_name,
                last_name=last_name,
                email=email,
                password_hash=(
                    AuthService.hash_password(password)
                ),
                role="admin",
                is_admin=True,
                is_active=True,
                email_verified=True,
            )

            db.add(user)
            db.commit()

            password_created = True

            print(f"[OK] Administrador creado: {email}")

        else:

            changed = False

            if user.role != "admin":
                user.role = "admin"
                changed = True

            if not user.is_admin:
                user.is_admin = True
                changed = True

            if not user.is_active:
                user.is_active = True
                changed = True

            if os.getenv("ADMIN_PASSWORD"):
                user.password_hash = (
                    AuthService.hash_password(password)
                )
                changed = True
                print("[OK] Contraseña actualizada.")

            if changed:
                db.commit()
                print(
                    f"[OK] Usuario existente promovido "
                    f"a admin: {email}"
                )
            else:
                print(
                    f"[OK] El administrador ya existe: "
                    f"{email} (sin cambios)"
                )

        if generated and password_created:
            print()
            print("=" * 50)
            print("CONTRASEÑA GENERADA (se muestra una sola vez):")
            print(f"  {password}")
            print("Cámbiala desde Mi Perfil al primer ingreso.")
            print("=" * 50)

    finally:
        db.close()


if __name__ == "__main__":
    main()
