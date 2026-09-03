#!/usr/bin/env python3
"""
Activa manualmente el plan Pro de un usuario.

Uso en Render (Shell):
    python scripts/activate_paid_plan.py arnaldoia66@gmail.com 30
"""

import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from database.session import SessionLocal
from models.user import User
from services.entitlements import Entitlements

def activate_plan(email, days=30):
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email == email).first()
        if not user:
            print(f"[ERROR] Usuario no encontrado: {email}")
            return False

        print(f"[INFO] Usuario: {user.email} (ID: {user.id})")
        
        Entitlements.activate_paid(
            db,
            user.id,
            days=days,
            source="manual_activation",
        )
        db.commit()

        status = Entitlements.get_status(user.id)
        print(f"[OK] Plan activado por {days} días")
        print(f"[INFO] Nuevo estado: {status}")
        return True

    except Exception as e:
        db.rollback()
        print(f"[ERROR] {e}")
        return False
    finally:
        db.close()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python scripts/activate_paid_plan.py <email> [días]")
        sys.exit(1)

    email = sys.argv[1]
    days = int(sys.argv[2]) if len(sys.argv) > 2 else 30
    activate_plan(email, days)