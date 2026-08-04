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
import shutil
import subprocess
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

# JavaScript: un solo error de sintaxis mata toda la página
# (caso real: planning.js con un "});" huérfano dejaba el
# selector de cursos pegado en "Cargando cursos...")
js_errors = []

if shutil.which("node"):

    js_dir = os.path.join(ROOT, "static", "js")

    if os.path.isdir(js_dir):

        for filename in sorted(os.listdir(js_dir)):

            if not filename.endswith(".js"):
                continue

            if "copia" in filename or "CHAT" in filename:
                continue  # respaldos, no se cargan en páginas

            path = os.path.join(js_dir, filename)
            # vm.Script parsea como SCRIPT CLÁSICO de navegador.
            # node --check parsea como módulo CommonJS y da falsos
            # positivos (ej: acepta "return" a nivel top, ilegal en
            # navegador — bug real que mató planning.js).
            result = subprocess.run(
                [
                    "node", "-e",
                    "const vm=require('vm');"
                    f"new vm.Script(require('fs').readFileSync("
                    f"'{path}','utf8'));",
                ],
                capture_output=True, text=True
            )

            if result.returncode != 0:
                js_errors.append(filename)

    check(
        "Todos los .js de static/js parsean",
        not js_errors,
        "; ".join(js_errors[:3])
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
    "/admin/comercial",
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

# Páginas legales públicas (v3.1.4 — requisito comercial Chile)
r = client.get("/terminos")

check(
    "Anónimo en /terminos -> 200 (Ley 19.628)",
    r.status_code == 200 and b"Ley" in r.data,
    f"recibió {r.status_code}"
)

r = client.get("/privacidad")

check(
    "Anónimo en /privacidad -> 200 (Ley 21.719)",
    r.status_code == 200 and b"21.719" in r.data,
    f"recibió {r.status_code}"
)

# Landing con Open Graph (compartir por WhatsApp)
r = client.get("/")

check(
    "Landing incluye Open Graph + imagen og-cover",
    r.status_code == 200
    and b'property="og:title"' in r.data
    and b"og-cover.png" in r.data,
    f"recibió {r.status_code}"
)

# Botón de pago apunta al WhatsApp real configurado (v3.1.4)
_ps = open(
    os.path.join(ROOT, "templates", "plan_status.html"),
    encoding="utf-8"
).read()

check(
    "Mi Plan usa config.WHATSAPP_NUMBER (sin placeholder)",
    "56900000000" not in _ps and "config.WHATSAPP_NUMBER" in _ps,
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
# 9. Regresión: /planning/generate acepta las claves que
#    envía planning.js (español) — bug "Campos obligatorios
#    faltantes: course, subject, unit" (v3.1.3+)
# ==========================================================

print("\n=== 9. Generate planning con claves reales del JS ===")

login(ADMIN_ID, "admin", "admin@verify.cl")

import routes.planning as _planning_routes

_captured = {}


class _FakePlanningService:

    def generate(self, data):
        _captured.update(data)
        return {"success": True, "content": "PLAN_OK"}


_real_ps = _planning_routes.planning_service
_planning_routes.planning_service = _FakePlanningService()

_csrf_prev = app_module.app.config.get("WTF_CSRF_ENABLED", True)
app_module.app.config["WTF_CSRF_ENABLED"] = False

try:

    # 9.1 Payload EXACTO que envía planning.js (buildPayload)
    r = client.post("/planning/generate", json={
        "curso": "5° Básico",
        "asignatura": "Tecnología",
        "unidad": "Unidad 2",
        "objetivos": ["OA 2"],
        "tema": "gráficos",
        "duracion": "45 minutos",
        "tipo": "Aprendizaje Basado en Proyectos",
        "metodologia": "Aprendizaje Activo",
        "evaluacion": "Formativa",
        "recursos": "PPT",
        "observaciones": "",
    })
    _body = r.get_json() or {}

    check(
        "/planning/generate acepta claves en español (JS real)",
        r.status_code == 200 and _body.get("success") is True,
        f"status={r.status_code} body={str(_body)[:120]}"
    )

    check(
        "Servicio recibió curso/asignatura/unidad/objetivos",
        _captured.get("curso") == "5° Básico"
        and _captured.get("asignatura") == "Tecnología"
        and _captured.get("unidad") == "Unidad 2"
        and _captured.get("objetivos") == ["OA 2"],
        f"captured={str(_captured)[:140]}"
    )

    # 9.2 Compatibilidad: aliases en inglés también entran
    _captured.clear()
    r = client.post("/planning/generate", json={
        "course": "5° Básico",
        "subject": "Tecnología",
        "unit": "Unidad 2",
        "objectives": ["OA 2"],
    })
    _body = r.get_json() or {}

    check(
        "/planning/generate traduce aliases en inglés",
        r.status_code == 200
        and _body.get("success") is True
        and _captured.get("curso") == "5° Básico"
        and _captured.get("objetivos") == ["OA 2"],
        f"status={r.status_code} captured={str(_captured)[:120]}"
    )

    # 9.3 Payload incompleto sigue rechazándose (400)
    r = client.post("/planning/generate", json={"tema": "x"})
    _body = r.get_json() or {}

    check(
        "/planning/generate rechaza payload incompleto (400)",
        r.status_code == 400
        and (
            "obligatorios" in str(_body.get("error") or "")
            or "obligatorios" in str(_body.get("message") or "")
        ),
        f"status={r.status_code} body={str(_body)[:120]}"
    )

    # 9.4 Generar con usuario trial CONSUME cuota (contador 0→1)
    _db2 = _SL()
    _ctx2 = app_module.app.app_context()
    _ctx2.push()

    try:

        _email2 = f"quota_{_dt.utcnow().timestamp():.0f}@verify.local"
        _u2 = _User(
            first_name="Quota",
            last_name="Test",
            email=_email2,
            password_hash="verify-only",
            role="teacher",
        )
        _db2.add(_u2)
        _db2.commit()
        _db2.refresh(_u2)

        _Ent.ensure_default_plans(_db2)
        _sub2 = _Ent.create_trial(_db2, _u2)

        login(str(_u2.id), "teacher", _email2)

        r = client.post("/planning/generate", json={
            "curso": "5° Básico",
            "asignatura": "Tecnología",
            "unidad": "Unidad 2",
            "objetivos": ["OA 2"],
        })
        _body = r.get_json() or {}

        _db2.refresh(_sub2)

        check(
            "Generación exitosa consume cuota del trial (0→1)",
            r.status_code == 200
            and _body.get("success") is True
            and _sub2.generations_used == 1,
            f"status={r.status_code} used={_sub2.generations_used}"
        )

        _db2.query(_US).filter(_US.user_id == str(_u2.id)).delete()
        _db2.delete(_u2)
        _db2.commit()

    finally:

        _db2.close()
        _ctx2.pop()

    login(ADMIN_ID, "admin", "admin@verify.cl")

finally:

    _planning_routes.planning_service = _real_ps
    app_module.app.config["WTF_CSRF_ENABLED"] = _csrf_prev


# ==========================================================
# 10. UX unificada módulos de generación (v3.1.5)
# ==========================================================

print("\n=== 10. UX unificada: evaluation/guides/rubrics/pie ===")

# 10.1 CSS compartido existe con las piezas clave
_guicss_path = os.path.join(ROOT, "static", "css", "generation-ui.css")
_guicss = open(_guicss_path, encoding="utf-8").read() \
    if os.path.exists(_guicss_path) else ""

check(
    "generation-ui.css existe (loader + markdown + toast)",
    ".loader-overlay.active" in _guicss
    and ".loader-content" in _guicss
    and ".loader-hint" in _guicss
    and ".generation-markdown" in _guicss
    and ".toast.show" in _guicss,
)

# 10.2-10.5 Plantillas: marked, css compartido, loader profesional,
# contenedor markdown y cache-busting
for _mod, _res_id in [
    ("guides", "guideResult"),
    ("rubrics", "rubricResult"),
    ("pie", "pieResult"),
    ("evaluation", "evaluationResult"),
]:

    _tpl = open(
        os.path.join(ROOT, "templates", f"{_mod}.html"),
        encoding="utf-8"
    ).read()

    check(
        f"{_mod}.html: marked + generation-ui.css + loader pro + "
        f"div markdown + cache-bust",
        "marked.min.js" in _tpl
        and "generation-ui.css" in _tpl
        and "loader-content" in _tpl
        and "loader-hint" in _tpl
        and "No cierres esta ventana" in _tpl
        and f'result-box generation-markdown" id="{_res_id}"' in _tpl
        and "<pre" not in _tpl
        and "css/dashboard.css', v=config.APP_VERSION" in _tpl,
    )

# 10.6 evaluation.html tiene cascada curricular (selects, no inputs
# de texto libre) y toast propio
_eval_tpl = open(
    os.path.join(ROOT, "templates", "evaluation.html"),
    encoding="utf-8"
).read()

check(
    "evaluation.html: selects en cascada + toast + campo preguntas",
    '<select id="curso"' in _eval_tpl
    and '<select id="asignatura"' in _eval_tpl
    and '<select id="unidad"' in _eval_tpl
    and '<select id="objetivo"' in _eval_tpl
    and 'id="toast"' in _eval_tpl
    and 'id="preguntas"' in _eval_tpl,
)

# 10.7 JS: renderMarkdown + lastGeneratedMarkdown + copia desde
# la fuente markdown en los 4 módulos
for _js in ["evaluation", "guides", "rubrics", "pie"]:

    _src = open(
        os.path.join(ROOT, "static", "js", f"{_js}.js"),
        encoding="utf-8"
    ).read()

    check(
        f"{_js}.js: renderMarkdown + lastGeneratedMarkdown + "
        f"clearResult con innerHTML",
        "function renderMarkdown" in _src
        and "lastGeneratedMarkdown" in _src
        and "result.innerHTML = renderMarkdown" in _src
        and (
            'result.innerHTML = ""' in _src
            or 'result.innerHTML=""' in _src
        )
        and "window.marked" in _src,
    )

# 10.8 evaluation.js: cascada curricular + loader por clase
_eval_js = open(
    os.path.join(ROOT, "static", "js", "evaluation.js"),
    encoding="utf-8"
).read()

check(
    "evaluation.js: cascada curricular + loader .active + "
    "botones btn-action",
    "populateSelect" in _eval_js
    and "/planning/api/curriculum" in _eval_js
    and 'classList.add("active")' in _eval_js
    and 'classList.remove("active")' in _eval_js
    and "btn-action btn-open" in _eval_js,
)

# 10.9 APP_VERSION actualizada (cache-busting de estáticos)
_cfg = open(
    os.path.join(ROOT, "config.py"),
    encoding="utf-8"
).read()

check(
    "APP_VERSION = 3.3.0 (cache-busting)",
    'APP_VERSION = "3.3.0"' in _cfg,
)

# 10.10 Páginas de los 4 módulos renderizan con la nueva UX
for _url, _res_id in [
    ("/evaluation/", "evaluationResult"),
    ("/guides/", "guideResult"),
    ("/rubrics/", "rubricResult"),
    ("/pie/", "pieResult"),
]:

    r = client.get(_url)

    check(
        f"GET {_url} sirve UX unificada",
        r.status_code == 200
        and b"generation-markdown" in r.data
        and b"marked.min.js" in r.data
        and b"loader-content" in r.data
        and _res_id.encode() in r.data,
        f"recibió {r.status_code}"
    )


# ==========================================================
# 11. Dashboard: tarjetas activas + actividad reciente
# ==========================================================

print("\n=== 11. Dashboard: tarjetas y actividad reciente ===")

# 11.1 Ninguna tarjeta de módulo operativo dice "Próximamente"
_dash_tpl = open(
    os.path.join(ROOT, "templates", "dashboard.html"),
    encoding="utf-8"
).read()

check(
    "dashboard.html: sin 'Próximamente' en módulos operativos",
    "coming-soon" not in _dash_tpl
    and "Próximamente" not in _dash_tpl
    and "evaluation.index" in _dash_tpl
    and "rubrics.index" in _dash_tpl
    and "pie.index" in _dash_tpl,
)

# 11.2 Actividad reciente es dinámica (loop Jinja) con fallback
check(
    "dashboard.html: actividad reciente dinámica",
    "recent_activity" in _dash_tpl
    and "activity-list" in _dash_tpl
    and "for item in recent_activity" in _dash_tpl
    and "Aún no existen actividades" in _dash_tpl,
)

# 11.3 La ruta entrega recent_activity al template
_dash_route = open(
    os.path.join(ROOT, "routes", "dashboard.py"),
    encoding="utf-8"
).read()

check(
    "routes/dashboard.py: _recent_activity con metadatos por tipo",
    "_recent_activity" in _dash_route
    and "_ACTIVITY_META" in _dash_route
    and "list_documents" in _dash_route
    and "recent_activity=_recent_activity" in _dash_route,
)

# 11.4 CSS de la lista de actividad existe
_dash_css = open(
    os.path.join(ROOT, "static", "css", "dashboard.css"),
    encoding="utf-8"
).read()

check(
    "dashboard.css: estilos activity-list/activity-icon",
    ".activity-list" in _dash_css
    and ".activity-item" in _dash_css
    and ".activity-icon.blue" in _dash_css,
)

# 11.5 E2E: documento recién creado aparece en el dashboard
from services.persistence_service import persistence_service as _psvc

_doc_id = _psvc.save_generated_document(
    user_id=str(ADMIN_ID),
    school_id=None,
    document_type="planning",
    payload={
        "curso": "7° Básico",
        "asignatura": "Historia",
        "unidad": "Unidad X",
        "tema": "ActividadRecienteVerify",
    },
    result={"content": "contenido de prueba actividad"},
)

try:

    r = client.get("/dashboard/")

    check(
        "GET /dashboard/ muestra el documento en Actividad reciente",
        r.status_code == 200
        and b"activity-list" in r.data
        and "Planning - Historia".encode() in r.data,
        f"recibió {r.status_code}"
    )

finally:

    from database.session import SessionLocal as _SL3
    from models.document import Document as _Doc3

    _db3 = _SL3()

    try:

        _db3.query(_Doc3).filter(_Doc3.id == _doc_id).delete()
        _db3.commit()

    finally:

        _db3.close()


# ==========================================================
# 12. Pagos Mercado Pago — Suscripciones (v3.2)
# ==========================================================

print("\n=== 12. Pagos: Mercado Pago Suscripciones ===")

# 12.1 Archivos del lote con piezas clave
_mp_svc = open(
    os.path.join(ROOT, "services", "mercadopago_service.py"),
    encoding="utf-8"
).read() if os.path.exists(
    os.path.join(ROOT, "services", "mercadopago_service.py")
) else ""

_pay_routes = open(
    os.path.join(ROOT, "routes", "payments.py"),
    encoding="utf-8"
).read() if os.path.exists(
    os.path.join(ROOT, "routes", "payments.py")
) else ""

check(
    "mercadopago_service.py: preapproval + authorized_payments "
    "+ firma HMAC",
    "create_subscription" in _mp_svc
    and "get_preapproval" in _mp_svc
    and "get_authorized_payment" in _mp_svc
    and "verify_signature" in _mp_svc
    and "api.mercadopago.com" in _mp_svc
    and "external_reference" in _mp_svc,
)

check(
    "routes/payments.py: checkout + return + webhook + "
    "idempotencia",
    "def checkout" in _pay_routes
    and "def return_page" in _pay_routes
    and "def webhook" in _pay_routes
    and "process_mp_webhook" in _pay_routes
    and "PaymentEvent" in _pay_routes
    and "activate_paid" in _pay_routes,
)

# 12.2 Config: claves MP y versión
check(
    "config.py: claves MP + APP_VERSION 3.3.0",
    "MERCADOPAGO_ACCESS_TOKEN" in _cfg
    and "MERCADOPAGO_WEBHOOK_SECRET" in _cfg
    and "MERCADOPAGO_SUCCESS_URL" in _cfg
    and 'APP_VERSION = "3.3.0"' in _cfg,
)

# 12.3 Cableado en app.py
_app_src = open(
    os.path.join(ROOT, "app.py"),
    encoding="utf-8"
).read()

check(
    "app.py: blueprint payments + webhook público + CSRF exempt",
    "from routes.payments import payments" in _app_src
    and "app.register_blueprint(payments)" in _app_src
    and "csrf.exempt(payments)" in _app_src
    and '"payments.webhook"' in _app_src,
)

# 12.4 Modelo de idempotencia
_pay_model = open(
    os.path.join(ROOT, "models", "payment_event.py"),
    encoding="utf-8"
).read() if os.path.exists(
    os.path.join(ROOT, "models", "payment_event.py")
) else ""

check(
    "payment_event.py: event_key único + provider",
    "payment_events" in _pay_model
    and "unique=True" in _pay_model
    and "event_key" in _pay_model
    and "provider" in _pay_model,
)

# 12.5 plan_status.html: botón de suscripción
_plan_tpl = open(
    os.path.join(ROOT, "templates", "plan_status.html"),
    encoding="utf-8"
).read()

check(
    "plan_status.html: botón Mercado Pago + respaldo WhatsApp",
    "payments.checkout" in _plan_tpl
    and "config.MERCADOPAGO_ACCESS_TOKEN" in _plan_tpl
    and "muy pronto" not in _plan_tpl,
)

# 12.6 Firma HMAC: vector conocido
import hashlib as _hl
import hmac as _hm

from services.mercadopago_service import (
    MercadoPagoService as _MPS,
)

_ctx3 = app_module.app.app_context()
_ctx3.push()

try:

    _secret_prev = app_module.app.config.get(
        "MERCADOPAGO_WEBHOOK_SECRET", ""
    )

    app_module.app.config["MERCADOPAGO_WEBHOOK_SECRET"] = (
        "secreto-verify"
    )

    _manifest = "id:12345;request-id:req-9;ts:1700000000;"
    _good = _hm.new(
        b"secreto-verify",
        _manifest.encode("utf-8"),
        _hl.sha256,
    ).hexdigest()

    check(
        "Firma webhook: acepta HMAC válido, rechaza inválido",
        _MPS.verify_signature(
            f"ts=1700000000,v1={_good}", "req-9", "12345"
        ) is True
        and _MPS.verify_signature(
            "ts=1700000000,v1=deadbeef", "req-9", "12345"
        ) is False,
    )

    # 12.7 Webhook con firma incorrecta → 401
    r = client.post(
        "/payments/webhook",
        json={"type": "subscription_preapproval",
              "data": {"id": "x"}},
        headers={"x-signature": "ts=1,v1=bad",
                 "x-request-id": "r"},
    )

    check(
        "POST /payments/webhook con firma mala → 401",
        r.status_code == 401,
        f"recibió {r.status_code}"
    )

    app_module.app.config["MERCADOPAGO_WEBHOOK_SECRET"] = ""

    # 12.8 E2E: webhook authorized activa el Plan Pro
    # (API de MP mockeada; idempotencia incluida)
    from models.payment_event import PaymentEvent as _PE
    from models.user_subscription import (
        UserSubscription as _US12,
    )

    _real_get_pre = _MPS.get_preapproval
    _MPS.get_preapproval = staticmethod(lambda pid: {
        "status": "authorized",
        "external_reference": str(ADMIN_ID),
    })

    try:

        r = client.post(
            "/payments/webhook",
            json={
                "type": "subscription_preapproval",
                "data": {"id": "preapproval-verify-1"},
            },
        )

        _db4 = _SL3()

        try:

            _sub = _db4.query(_US12).filter(
                _US12.user_id == str(ADMIN_ID)
            ).first()

            _ev = _db4.query(_PE).filter(
                _PE.event_key ==
                "subscription_preapproval:preapproval-verify-1"
            ).first()

            check(
                "Webhook authorized → Plan Pro activo + "
                "auditoría PaymentEvent",
                r.status_code == 200
                and r.get_json().get("status") == "activated"
                and _sub is not None
                and _sub.status == "active"
                and _sub.source == "mercadopago"
                and _ev is not None
                and _ev.action == "activated",
                f"status={r.status_code} sub="
                f"{getattr(_sub, 'status', None)}"
            )

            # Mismo evento otra vez → duplicate (no reactiva)
            r2 = client.post(
                "/payments/webhook",
                json={
                    "type": "subscription_preapproval",
                    "data": {"id": "preapproval-verify-1"},
                },
            )

            check(
                "Webhook duplicado → idempotente (duplicate)",
                r2.status_code == 200
                and r2.get_json().get("status") == "duplicate",
            )

        finally:

            _db4.close()

    finally:

        _MPS.get_preapproval = _real_get_pre

    # 12.9 Checkout sin MP configurado → redirige a Mi Plan
    r = client.get("/payments/checkout")

    check(
        "GET /payments/checkout responde redirect seguro",
        r.status_code == 302,
        f"recibió {r.status_code}"
    )

    # 12.10 Página de retorno renderiza
    r = client.get("/payments/return")

    check(
        "GET /payments/return renderiza confirmación",
        r.status_code == 200
        and "suscribirte".encode() in r.data,
        f"recibió {r.status_code}"
    )

    app_module.app.config["MERCADOPAGO_WEBHOOK_SECRET"] = (
        _secret_prev
    )

finally:

    _ctx3.pop()


# ==========================================================
# 13. Panel Comercial (v3.3)
# ==========================================================

print("\n=== 13. Panel Comercial ===")


def _read_rel(*parts):
    path = os.path.join(ROOT, *parts)
    if not os.path.exists(path):
        return ""
    return open(path, encoding="utf-8").read()


_ac_route = _read_rel("routes", "admin_comercial.py")
_ac_tpl = _read_rel("templates", "admin_comercial.html")
_ac_js = _read_rel("static", "js", "admin_comercial.js")

# 13.1 Archivos del lote con piezas clave
check(
    "admin_comercial.py: página + resumen + usuarios + "
    "eventos + PaymentEvent",
    "def comercial_page" in _ac_route
    and "def resumen" in _ac_route
    and "def usuarios" in _ac_route
    and "def eventos" in _ac_route
    and "PaymentEvent" in _ac_route
    and 'role_required("admin")' in _ac_route,
)

check(
    "admin_comercial.html: panel + KPIs + modal + CSRF meta",
    "Panel Comercial" in _ac_tpl
    and "COMERCIAL_CONFIG" in _ac_tpl
    and "csrf-token" in _ac_tpl
    and "planModal" in _ac_tpl
    and "admin_comercial.js" in _ac_tpl
    and "admin_comercial.css" in _ac_tpl,
)

check(
    "admin_comercial.js: fetch con token CSRF + activación",
    "X-CSRFToken" in _ac_js
    and "btn-activate" in _ac_js
    and "planUrl" in _ac_js,
)

check(
    "admin_comercial.css existe",
    os.path.exists(
        os.path.join(
            ROOT, "static", "css", "admin_comercial.css"
        )
    ),
)

# 13.2 Cableado en app.py
_app_src13 = _read_rel("app.py")

check(
    "app.py: blueprint admin_comercial registrado",
    "from routes.admin_comercial import admin_comercial"
    in _app_src13
    and "app.register_blueprint(admin_comercial)"
    in _app_src13,
)

# 13.3 Sidebar: enlace dentro del bloque solo-admin
_sidebar13 = _read_rel(
    "templates", "partials", "sidebar_menu.html"
)

_i_admin = _sidebar13.find("session.get('role') == 'admin'")
_i_link = _sidebar13.find("admin_comercial.comercial_page")
_i_endif = _sidebar13.find("{% endif %}", _i_link)

check(
    "sidebar: Comercial visible solo para admin",
    _i_admin != -1
    and _i_admin < _i_link != -1
    and _i_link < _i_endif,
)

# 13.4 Bugfix CSRF en módulo Usuarios (M-09)
_au_tpl13 = _read_rel("templates", "admin_users.html")
_au_js13 = _read_rel("static", "js", "admin_users.js")

check(
    "Bugfix CSRF M-09: meta token + header X-CSRFToken",
    'name="csrf-token"' in _au_tpl13
    and "X-CSRFToken" in _au_js13,
)

# 13.5 Versión
check(
    "config.py: APP_VERSION 3.3.0",
    'APP_VERSION = "3.3.0"' in _cfg,
)

# 13.6 E2E admin: página, APIs y token CSRF real
import re as _re13

login(ADMIN_ID, "admin", "admin@verify.cl")

r = client.get("/admin/comercial")
_body13 = r.data.decode(errors="ignore")

check(
    "GET /admin/comercial → 200 con panel",
    r.status_code == 200 and "Panel Comercial" in _body13,
    f"recibió {r.status_code}"
)

_m13 = _re13.search(
    r'name="csrf-token" content="([^"]+)"', _body13
)
_csrf13 = _m13.group(1) if _m13 else ""

check(
    "Página comercial entrega token CSRF en meta",
    bool(_csrf13),
)

r = client.get("/admin/api/comercial/resumen")
_j13 = r.get_json(silent=True) or {}
_k13 = _j13.get("kpis", {})

check(
    "API resumen: KPIs completos + activación MP del mes",
    r.status_code == 200
    and _j13.get("success")
    and all(
        k in _k13 for k in (
            "usuarios", "trials", "pro_activos",
            "expirados", "activaciones_mes",
        )
    )
    and _k13.get("activaciones_mes", 0) >= 1,
    f"status={r.status_code} kpis={sorted(_k13)}",
)

r = client.get("/admin/api/comercial/usuarios")
_j13 = r.get_json(silent=True) or {}
_items13 = _j13.get("items", [])

check(
    "API usuarios: fila comercial del profe de prueba",
    r.status_code == 200
    and _j13.get("success")
    and any(
        i.get("email") == "profe@verify.cl"
        and "status_label" in i
        and "days_left" in i
        and "source_label" in i
        for i in _items13
    ),
    f"status={r.status_code} total={_j13.get('total')}",
)

r = client.get("/admin/api/comercial/eventos")
_j13 = r.get_json(silent=True) or {}

check(
    "API eventos: pipeline muestra la activación MP (12.8)",
    r.status_code == 200
    and _j13.get("success")
    and _j13.get("total", 0) >= 1
    and any(
        i.get("action") == "activated"
        and i.get("provider") == "mercadopago"
        for i in _j13.get("items", [])
    ),
    f"status={r.status_code} total={_j13.get('total')}",
)

# 13.7 Activación manual con CSRF (bugfix E2E M-09)
from models.user_subscription import (
    UserSubscription as _US13,
)

r = client.put(
    f"/admin/api/usuarios/{PROFE_ID}/plan",
    json={"days": 30},
    headers={"X-CSRFToken": _csrf13},
)
_j13 = r.get_json(silent=True) or {}

_db13 = _SL3()

try:

    _sub13 = _db13.query(_US13).filter(
        _US13.user_id == str(PROFE_ID)
    ).first()

finally:

    _db13.close()

check(
    "PUT plan con CSRF → Plan Pro activo (origen manual)",
    r.status_code == 200
    and _j13.get("success")
    and _j13.get("plan", {}).get("status") == "active"
    and _sub13 is not None
    and _sub13.status == "active"
    and _sub13.source == "manual",
    f"status={r.status_code} json={_j13.get('plan')}",
)

r = client.put(
    f"/admin/api/usuarios/{PROFE_ID}/plan",
    json={"days": 30},
)

check(
    "PUT plan sin CSRF → 400 (protección intacta)",
    r.status_code == 400,
    f"recibió {r.status_code}",
)

# 13.8 Acceso por rol
login(PROFE_ID, "teacher", "profe@verify.cl")

r = client.get("/admin/comercial")
_r_api = client.get("/admin/api/comercial/resumen")

check(
    "Teacher recibe 403 en panel y API comercial",
    r.status_code == 403 and _r_api.status_code == 403,
    f"página={r.status_code} api={_r_api.status_code}",
)

login(ADMIN_ID, "admin", "admin@verify.cl")
_admin_sees_c = (
    "/admin/comercial"
    in client.get("/dashboard/").data.decode()
)

login(PROFE_ID, "teacher", "profe@verify.cl")
_teacher_sees_c = (
    "/admin/comercial"
    in client.get("/dashboard/").data.decode()
)

check(
    "Link Comercial solo para admin",
    _admin_sees_c and not _teacher_sees_c,
    f"admin={_admin_sees_c}, teacher={_teacher_sees_c}",
)


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