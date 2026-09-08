#!/usr/bin/env python3
"""
AulaMind Enterprise 3.0 — Smoke Test Post-Deploy v2 (rutas reales)

Ajustado a la arquitectura real: el blueprint payments NO usa
url_prefix, sus rutas viven en raiz:
  /webhook   (GET challenge -> 200 {"status":"ok"})
  /webhook   (POST sin firma -> 200 ignored o 401)
  /checkout  (GET sin sesion -> 302 al login)
  /return    (GET sin sesion -> 302 al login)

Uso:
    python smoke_test_v2.py

Salida: codigo 0 si todo OK, 1 si hay fallos.
"""

import json
import sys
import urllib.request
import urllib.error
import ssl

BASE = "https://www.aulamind.cl"
CHECKS = []


def check(name):
    def deco(fn):
        CHECKS.append((name, fn))
        return fn
    return deco


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def req(method, path, data=None, headers=None):
    url = BASE + path
    body = json.dumps(data).encode() if data is not None else None
    r = urllib.request.Request(url, data=body, method=method)
    r.add_header("Content-Type", "application/json")
    for k, v in (headers or {}).items():
        r.add_header(k, v)
    opener = urllib.request.build_opener(
        NoRedirect(), urllib.request.HTTPSHandler(context=ssl.create_default_context())
    )
    try:
        with opener.open(r, timeout=20) as resp:
            return resp.status, dict(resp.headers), resp.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as e:
        return e.code, dict(e.headers), e.read().decode("utf-8", "replace")
    except Exception as e:
        return None, {}, f"__ERROR__ {e}"


@check("1. Health endpoint")
def t_health():
    s, _, b = req("GET", "/health")
    if s != 200:
        return False, f"esperado 200, llego {s}"
    try:
        d = json.loads(b)
        return True, f"app={d.get('application')} v{d.get('version')} status={d.get('status')}"
    except Exception:
        return False, f"respuesta no es JSON: {b[:120]}"


@check("2. Landing publica")
def t_landing():
    s, _, _ = req("GET", "/")
    return (s == 200, f"HTTP {s}" if s == 200 else f"esperado 200, llego {s}")


@check("3. Pagina de login")
def t_login_page():
    s, _, _ = req("GET", "/auth/login")
    return (s == 200, f"HTTP {s}" if s == 200 else f"esperado 200, llego {s}")


@check("4. Webhook MP — GET challenge (/webhook)")
def t_webhook_get():
    s, _, b = req("GET", "/webhook")
    if s == 200 and '"ok"' in b:
        return True, "challenge respondido OK (200)"
    return False, f"HTTP {s} body={b[:100]!r}"


@check("5. Webhook MP — POST sin firma")
def t_webhook_post():
    s, _, b = req("POST", "/webhook", data={"type": "test", "data": {"id": "smoke"}})
    if s == 200:
        return True, f"recibido (200) — respuesta: {b[:80]}"
    if s == 401:
        return True, "firma rechazada con 401 (secreto configurado — modo estricto)"
    return False, f"HTTP inesperado {s}: {b[:100]}"


@check("6. /checkout exige sesion (302 al login)")
def t_checkout_guard():
    s, h, _ = req("GET", "/checkout")
    loc = h.get("Location", "")
    if s in (301, 302) and "/auth/login" in loc:
        return True, f"HTTP {s} -> {loc}"
    return False, f"esperado redirect a login, llego HTTP {s}"


@check("7. /return exige sesion (302 al login)")
def t_return_guard():
    s, h, _ = req("GET", "/return")
    loc = h.get("Location", "")
    if s in (301, 302) and "/auth/login" in loc:
        return True, f"HTTP {s} -> {loc}"
    return False, f"esperado redirect a login, llego HTTP {s}"


@check("8. Modalidades de planificacion (401 sin sesion = ruta viva)")
def t_modalities():
    s, _, b = req("GET", "/planning/api/planning/modalities")
    if s == 401:
        return True, "ruta viva, guardia de auth activa (401)"
    if s == 200:
        return True, "ruta publica, responde 200"
    return False, f"HTTP {s}: {b[:100]}"


def main():
    print("=" * 64)
    print("AulaMind — Smoke Test v2 (rutas reales, sin /payments/)")
    print(f"Objetivo: {BASE}")
    print("=" * 64)

    failed = 0
    for name, fn in CHECKS:
        try:
            ok, detail = fn()
        except Exception as e:
            ok, detail = False, f"excepcion: {e}"
        if not ok:
            failed += 1
        print(f"[{'PASS' if ok else 'FAIL'}] {name}\n       -> {detail}")

    print("=" * 64)
    if failed:
        print(f"RESULTADO: {failed} check(s) FALLARON")
        sys.exit(1)
    print("RESULTADO: 8/8 PASS — Deploy validado.")
    sys.exit(0)


if __name__ == "__main__":
    main()
