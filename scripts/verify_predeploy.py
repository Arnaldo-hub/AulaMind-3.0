"""
===========================================================
AulaMind Enterprise 3.0
scripts/verify_predeploy.py
-----------------------------------------------------------
Verificación pre-deploy.

Ejecuta ANTES de cada push a producción:

    python scripts/verify_predeploy.py

Chequeos:
    1. Sintaxis de todos los archivos .py
    2. Parseo Jinja2 de todos los templates
    3. Arranque de la app con SQLite temporal
    4. Todas las páginas principales responden 200
    5. Sin enlaces muertos (href="#")
    6. Enlace Usuarios visible solo para admin

Exit code 0 = todo OK, 1 = falló algo (no desplegar).

Autor:
Biotecno Chile
===========================================================
"""

import importlib
import os
import pkgutil
import py_compile
import sys
import tempfile

# ----------------------------------------------------------
# Raíz del proyecto (este script vive en scripts/)
# ----------------------------------------------------------

ROOT = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

sys.path.insert(0, ROOT)
os.chdir(ROOT)

os.environ.setdefault("OPENAI_API_KEY", "sk-test-dummy")

RESULTS = []


def check(name, ok, detail=""):
    RESULTS.append((ok, name, detail))
    icon = "[OK]  " if ok else "[FAIL]"
    line = f"{icon} {name}"
    if detail:
        line += f"  ({detail})"
    print(line)


# ==========================================================
# 1. Sintaxis Python
# ==========================================================

print("\n=== 1. Sintaxis Python ===")

py_errors = []

for folder, _, files in os.walk(ROOT):

    if any(skip in folder for skip in (
        ".git", "node_modules", "__pycache__", ".venv", "venv"
    )):
        continue

    for filename in files:

        if not filename.endswith(".py"):
            continue

        path = os.path.join(folder, filename)

        try:
            py_compile.compile(path, doraise=True)
        except py_compile.PyCompileError as ex:
            py_errors.append(f"{filename}: {ex}")

check(
    "Todos los .py compilan",
    not py_errors,
    "; ".join(py_errors[:3])
)


# ==========================================================
# 2. Templates Jinja2
# ==========================================================

print("\n=== 2. Templates Jinja2 ===")

from jinja2 import Environment, FileSystemLoader

env = Environment(
    loader=FileSystemLoader(
        os.path.join(ROOT, "templates")
    )
)

jinja_errors = []

for folder, _, files in os.walk(
    os.path.join(ROOT, "templates")
):

    for filename in files:

        if not filename.endswith(".html"):
            continue

        rel = os.path.relpath(
            os.path.join(folder, filename),
            os.path.join(ROOT, "templates")
        ).replace(os.sep, "/")

        try:
            env.get_template(rel)
        except Exception as ex:
            jinja_errors.append(f"{rel}: {ex}")

check(
    "Todos los templates parsean",
    not jinja_errors,
    "; ".join(jinja_errors[:3])
)


# ==========================================================
# 3-6. App completa con SQLite temporal
# ==========================================================

print("\n=== 3. Arranque de la app ===")

import config

tmp = tempfile.NamedTemporaryFile(
    suffix=".db", delete=False
)

config.Config.SQLALCHEMY_DATABASE_URI = (
    f"sqlite:///{tmp.name}"
)

import database.session as ds
importlib.reload(ds)

from database.base import Base
import models

for module in pkgutil.iter_modules(models.__path__):
    importlib.import_module(f"models.{module.name}")

import sqlalchemy

engine = sqlalchemy.create_engine(
    config.Config.SQLALCHEMY_DATABASE_URI
)

Base.metadata.create_all(engine)
ds.SessionLocal.configure(bind=engine)

from services.auth_service import AuthService
from models.user import User

db = ds.SessionLocal()

admin = User(
    first_name="Test", last_name="Admin",
    email="admin@verify.cl",
    password_hash=AuthService.hash_password(
        "Password123"
    ),
    role="admin", is_admin=True,
)

profe = User(
    first_name="Test", last_name="Profe",
    email="profe@verify.cl",
    password_hash=AuthService.hash_password(
        "Password123"
    ),
)

db.add_all([admin, profe])
db.commit()
ADMIN_ID, PROFE_ID = admin.id, profe.id
db.close()

try:
    import app as app_module
    check("La app arranca", True)
except Exception as ex:
    check("La app arranca", False, str(ex)[:120])
    print("\nLA APP NO ARRANCA - NO DESPLEGAR")
    sys.exit(1)

client = app_module.app.test_client()


def login(user_id, role, email):
    with client.session_transaction() as s:
        s["user_id"] = user_id
        s["role"] = role
        s["user_name"] = "Test User"
        s["email"] = email


# ==========================================================
# 4-5. Páginas y enlaces muertos
# ==========================================================

print("\n=== 4-5. Páginas y enlaces ===")

PAGES = [
    "/dashboard/",
    "/planning/",
    "/evaluation/",
    "/guides/",
    "/rubrics/",
    "/pie/",
    "/analytics/",
    "/curriculum/",
    "/admin/usuarios",
    "/auth/profile",
    "/auth/login",
    "/auth/forgot-password",
]

login(ADMIN_ID, "admin", "admin@verify.cl")

for path in PAGES:

    try:

        r = client.get(path)
        body = r.data.decode(errors="ignore")
        dead = 'href="#"' in body

        check(
            f"{path} -> {r.status_code}",
            r.status_code == 200 and not dead,
            "href=# muerto" if dead else ""
        )

    except Exception as ex:
        check(f"{path}", False, str(ex)[:80])


# ==========================================================
# 6. Visibilidad por rol
# ==========================================================

print("\n=== 6. Visibilidad por rol ===")

login(ADMIN_ID, "admin", "admin@verify.cl")
admin_sees = (
    "/admin/usuarios" in client.get("/dashboard/").data.decode()
)

login(PROFE_ID, "teacher", "profe@verify.cl")
teacher_sees = (
    "/admin/usuarios" in client.get("/dashboard/").data.decode()
)

check(
    "Link Usuarios solo para admin",
    admin_sees and not teacher_sees,
    f"admin={admin_sees}, teacher={teacher_sees}"
)

r = client.get("/admin/usuarios")
check(
    "Teacher recibe 403 en /admin/usuarios",
    r.status_code == 403,
    f"recibió {r.status_code}"
)

# /admin/health: JSON válido para admin, 403 para teacher
login(ADMIN_ID, "admin", "admin@verify.cl")
r = client.get("/admin/health")
try:
    health = r.get_json()
    health_ok = (
        r.status_code in (200, 503)
        and "status" in health
        and "checks" in health
    )
except Exception:
    health_ok = False
check(
    "GET /admin/health responde JSON válido",
    health_ok,
    f"status_code={r.status_code}"
)

login(PROFE_ID, "teacher", "profe@verify.cl")
r = client.get("/admin/health")
check(
    "Teacher recibe 403 en /admin/health",
    r.status_code == 403,
    f"recibió {r.status_code}"
)


# ==========================================================
# 7. Guardia global de autenticación (DT-016)
# ==========================================================

print("\n=== 7. Guardia global de autenticación ===")

# Anónimo: toda página protegida debe redirigir al login
with client.session_transaction() as s:
    s.clear()

PROTECTED = [
    "/planning/",
    "/evaluation/",
    "/guides/",
    "/rubrics/",
    "/pie/",
    "/analytics/",
    "/curriculum/",
    "/admin/usuarios",
    "/auth/profile",
    "/plan/",
]

for path in PROTECTED:

    r = client.get(path)
    location = r.headers.get("Location", "")

    check(
        f"Anónimo en {path} -> login",
        r.status_code in (301, 302) and "/auth/login" in location,
        f"recibió {r.status_code} -> {location[:50]}"
    )

# Anónimo: páginas públicas siguen abiertas
for path in ("/auth/login", "/auth/forgot-password", "/health"):

    r = client.get(path)

    check(
        f"Anónimo en {path} -> 200",
        r.status_code == 200,
        f"recibió {r.status_code}"
    )

# Anónimo: la raíz sirve la landing pública (v3.1)
r = client.get("/")

check(
    "Anónimo en / -> landing (200)",
    r.status_code == 200 and b"Prueba gratis" in r.data,
    f"recibió {r.status_code}"
)

# Con sesión: la raíz redirige al dashboard (v3.1)
login(ADMIN_ID, "admin", "admin@verify.cl")
r = client.get("/")

check(
    "Con sesión en / -> /dashboard/",
    r.status_code in (301, 302)
    and "/dashboard/" in r.headers.get("Location", ""),
    f"recibió {r.status_code}"
)

with client.session_transaction() as s:
    s.clear()

# Anónimo: API responde 401 JSON, nunca datos
r = client.get("/admin/api/usuarios")

check(
    "Anónimo en /admin/api/usuarios -> 401",
    r.status_code == 401,
    f"recibió {r.status_code}"
)

# ==========================================================
# 8. Motor de trial (v3.1)
# ==========================================================

print("\n=== 8. Motor de trial (v3.1) ===")

from datetime import datetime as _dt, timedelta as _td
from database.session import SessionLocal as _SL
from models.user import User as _User
from models.user_subscription import UserSubscription as _US
from services.entitlements import Entitlements as _Ent

_db = _SL()
_ctx = app_module.app.app_context()
_ctx.push()

try:

    _email = f"trialtest_{_dt.utcnow().timestamp():.0f}@verify.local"
    _user = _User(
        first_name="Trial",
        last_name="Test",
        email=_email,
        password_hash="verify-only",
        role="teacher",
    )
    _db.add(_user)
    _db.commit()
    _db.refresh(_user)

    # 8.1 Planes por defecto se siembran solos
    _plans = _Ent.ensure_default_plans(_db)
    check(
        "Planes Trial/Pro existen (seeding)",
        "Trial" in _plans and "Pro" in _plans,
        f"planes: {sorted(_plans.keys())}"
    )

    # 8.2 create_trial asigna trial de 3 días
    _sub = _Ent.create_trial(_db, _user)
    check(
        "create_trial crea suscripción trial",
        _sub.status == "trial" and _sub.ends_at > _dt.utcnow(),
        f"status={_sub.status} ends={_sub.ends_at}"
    )

    # 8.3 Trial fresco puede generar
    _res = _Ent.check_generation(str(_user.id))
    check(
        "Trial fresco permite generar",
        _res.get("allowed") is True and _res.get("reason") == "trial",
        f"reason={_res.get('reason')}"
    )

    # 8.4 record_generation consume cuota
    _Ent.record_generation(str(_user.id))
    _db.refresh(_sub)
    check(
        "record_generation incrementa contador",
        _sub.generations_used == 1,
        f"generations_used={_sub.generations_used}"
    )

    # 8.5 Trial vencido bloquea con razón trial_expired
    _sub.ends_at = _dt.utcnow() - _td(hours=1)
    _db.commit()
    _res = _Ent.check_generation(str(_user.id))
    check(
        "Trial vencido bloquea (trial_expired)",
        _res.get("allowed") is False and _res.get("reason") == "trial_expired",
        f"reason={_res.get('reason')}"
    )

    # 8.6 activate_paid reactiva como Plan Pro
    _Ent.activate_paid(_db, str(_user.id), days=30, source="verify")
    _res = _Ent.check_generation(str(_user.id))
    check(
        "activate_paid reactiva (paid)",
        _res.get("allowed") is True and _res.get("reason") == "paid",
        f"reason={_res.get('reason')}"
    )

    # 8.7 Admin siempre pasa, aunque no tenga suscripción
    _admin = _db.query(_User).filter(_User.role == "admin").first()
    if _admin is not None:
        _res = _Ent.check_generation(str(_admin.id))
        check(
            "Admin sin suscripción pasa igual (bypass)",
            _res.get("allowed") is True and _res.get("reason") == "admin",
            f"reason={_res.get('reason')}"
        )
    else:
        check("Admin existe en BD", False, "no hay usuario admin")

    # Limpieza: borrar datos de prueba
    _db.query(_US).filter(_US.user_id == str(_user.id)).delete()
    _db.delete(_user)
    _db.commit()

finally:

    _db.close()
    _ctx.pop()


# ==========================================================
# Reporte final
# ==========================================================

total = len(RESULTS)
fails = [r for r in RESULTS if not r[0]]

print("\n" + "=" * 50)

if fails:
    print(f"RESULTADO: {total - len(fails)}/{total} OK")
    print("HAY FALLOS - NO DESPLEGAR")
    sys.exit(1)

print(f"RESULTADO: {total}/{total} OK")
print("TODO VERDE - LISTO PARA DEPLOY")
sys.exit(0)
