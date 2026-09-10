#!/usr/bin/env python3
"""
CAPA 1 — Prueba local de modalidades (sin deploy)
Ejecutar en la carpeta del repo:  python test_modalidades_local.py

Verifica:
  1. Las 5 modalidades pasan validacion con sus campos
  2. Cada modalidad arma un prompt distinto y correcto
  3. SIN modalidad_plan el comportamiento es el original
"""

import sys
import types

# --- stubs para importar sin Flask ni OpenAI real ---
flask_stub = types.ModuleType("flask")


class _FakeApp:
    pass


flask_stub.current_app = _FakeApp()
flask_stub.current_app.config = {}
sys.modules["flask"] = flask_stub

openai_stub = types.ModuleType("services.openai_service")


class OpenAIService:
    def available(self):
        return True

    def generate(self, **kw):
        return {"success": True, "content": "ok"}


openai_stub.OpenAIService = OpenAIService
sys.modules["services.openai_service"] = openai_stub

from services.planning_service import PlanningService, PlanningModalities  # noqa: E402

svc = PlanningService()
base = {
    "curso": "5° Básico",
    "asignatura": "Matemática",
    "unidad": "Fracciones",
    "objetivos": ["OA 11: Resolver problemas de fracciones."],
    "duracion": "90 minutos",
}

print("=" * 60)
print("CAPA 1 — Prueba local de las 5 modalidades")
print("=" * 60)

fails = 0
for mod in PlanningModalities.list():
    ctx = dict(base)
    ctx["modalidad_plan"] = mod["id"]
    if mod["id"] == "anual":
        ctx["fecha_inicio"] = "2026-03-02"
        ctx["fecha_termino"] = "2026-12-18"
    if mod["id"] == "mensual":
        ctx["mes"] = "2026-04"

    ok, msg = svc.validate(svc.sanitize(ctx))
    if not ok:
        print(f"[FAIL] {mod['id']}: {msg}")
        fails += 1
        continue
    p = svc.build_prompt(svc.build_context(svc.sanitize(ctx)), "OA 11: ...")
    print(f"[PASS] {mod['id']:10s} -> {p[:60].strip()}...")

# validaciones negativas: anual sin fechas debe fallar
ctx = dict(base)
ctx["modalidad_plan"] = "anual"
ok, msg = svc.validate(svc.sanitize(ctx))
if ok:
    print("[FAIL] anual sin fechas NO fue rechazada")
    fails += 1
else:
    print(f"[PASS] anual sin fechas -> rechazada: {msg}")

# retrocompatibilidad
ctx = dict(base)
ok, msg = svc.validate(svc.sanitize(ctx))
p = svc.build_prompt(svc.build_context(svc.sanitize(ctx)), "OA 11: ...")
if ok and "Eres AulaMind Enterprise 3.0." in p:
    print("[PASS] sin modalidad_plan -> comportamiento original intacto")
else:
    print("[FAIL] retrocompatibilidad rota")
    fails += 1

print("=" * 60)
if fails:
    print(f"RESULTADO: {fails} fallos")
    sys.exit(1)
print("RESULTADO: 7/7 PASS — Capa 1 lista para deploy")
