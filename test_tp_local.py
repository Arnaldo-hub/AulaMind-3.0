#!/usr/bin/env python3
"""
Verificacion local del paquete TP (sin deploy).
Ejecutar desde la RAIZ del repo:  python test_tp_local.py
"""
import os
os.environ.setdefault("SECRET_KEY", "test-local")
from app import app
app.config["TESTING"] = True
app.config["WTF_CSRF_ENABLED"] = False
client = app.test_client()
with client.session_transaction() as s:
    s["user_id"] = "t1"; s["user_name"] = "T"
from urllib.parse import quote

fails = 0
cursos = client.get("/planning/api/curriculum/courses").get_json()["courses"]
tp = [c for c in cursos if "TP" in str(c)]
print("Cursos TP en dropdown:", tp)
if len(tp) != 2:
    print("[FAIL] Deben existir '3° Medio TP' y '4° Medio TP'")
    fails += 1

for curso, esperadas in [("3° Medio TP", 5), ("4° Medio TP", 6)]:
    subs = client.get(f"/planning/api/curriculum/subjects/{quote(curso)}").get_json()["subjects"]
    u = oa = 0
    for a in subs:
        units = client.get(f"/planning/api/curriculum/units/{quote(curso)}/{quote(a)}").get_json()["units"]
        if units:
            u += 1
            un = units[0]["name"] if isinstance(units[0], dict) else units[0]
            if client.get(f"/planning/api/curriculum/objectives/{quote(curso)}/{quote(a)}/{quote(un)}").get_json()["objectives"]:
                oa += 1
    ok = len(subs) == esperadas and u == esperadas and oa == esperadas
    print(f"[{'PASS' if ok else 'FAIL'}] {curso}: {len(subs)} especialidades | unidades {u} | OA {oa}")
    if not ok: fails += 1

# regresiones
for curso, min_esperado in [("3° Medio", 7), ("5° Básico", 11), ("NT1", 12)]:
    subs = client.get(f"/planning/api/curriculum/subjects/{quote(curso)}").get_json()["subjects"]
    ok = len(subs) >= min_esperado
    print(f"[{'PASS' if ok else 'FAIL'}] {curso}: {len(subs)} asignaturas (sin regresión)")
    if not ok: fails += 1

print("\nRESULTADO:", "TODO OK — listo para deploy" if fails == 0 else f"{fails} fallos")
