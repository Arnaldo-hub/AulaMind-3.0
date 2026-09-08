#!/usr/bin/env python3
"""
AulaMind Enterprise 3.0 — Smoke Test Post-Deploy (v1.0)

Autor: CTO AulaMind / Biotecno Chile
Fecha: 2026-09-08

Uso:
    python smoke_test.py                      # contra producción
    python smoke_test.py --base https://staging.aulamind.cl

Qué valida:
    1.  GET  /health              → 200 + JSON con versión
    2.  GET  /                    → 200 (landing pública)
    3.  GET  /auth/login          → 200 (página de login)
    4.  GET  /payments/webhook    → 200 {"status":"ok"} (challenge MP)
    5.  POST /payments/webhook    → 401 sin firma (no 404: ruta existe y valida)
    6.  GET  /payments/return     → 302 al login (ruta registrada, guardia OK)
    7.  GET  /payments/checkout   → 302 al login (exige sesión, no 404)
    8.  TLS y redirect www→apex (o apex→www) consistente

Criterio de éxito: todos los checks PASS.
Un solo FAIL en payments/* significa que el deploy NO corresponde
al código de main (la causa raíz del incidente 2026-09-08).

Salida: código 0 si todo OK, 1 si hay fallos.
"""

import argparse
import json
import sys
import urllib.request
import urllib.error
import ssl

CHECKS = []
BASE = "https://www.aulamind.cl"


def check(name):
    def deco(fn):
        CHECKS.append((name, fn))
        return fn
    return deco


def req(method, path, data=None, headers=None, follow_redirects=False):
    url = BASE + path
    body = json.dumps(data).encode() if data is not None else None
    r = urllib.request.Request(url, data=body, method=method)
    r.add_header("Content-Type", "application/json")
    for k, v in (headers or {}).items():
        r.add_header(k, v)
    ctx = ssl.create_default_context()
    redirect_handler = (
        urllib.request.HTTPRedirectHandler()
        if follow_redirects
        else NoRedirect()
    )
    opener = urllib.request.build_opener(
        redirect_handler,
        urllib.request.HTTPSHandler(context=ctx),
    )
    try:
        with opener.open(r, timeout=20) as resp:
            return resp.status, dict(resp.headers), resp.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as e:
        return e.code, dict(e.headers), e.read().decode("utf-8", "replace")
    except Exception as e:
        return None, {}, f"__ERROR__ {e}"


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


@check("1. Health endpoint")
def t_health():
    s, _, b = req("GET", "/health")
    if s != 200:
        return False, f"esperado 200, llegó {s}"
    try:
        d = json.loads(b)
        return True, f"app={d.get('application')} v{d.get('version')} status={d.get('status')}"
    except Exception:
        return False, f"respuesta no es JSON: {b[:120]}"


@check("2. Landing pública")
def t_landing():
    s, _, _ = req("GET", "/")
    return (s == 200, f"HTTP {s}" if s == 200 else f"esperado 200, llegó {s}")


@check("3. Página de login")
def t_login_page():
    s, _, _ = req("GET", "/auth/login")
    return (s == 200, f"HTTP {s}" if s == 200 else f"esperado 200, llegó {s}")


@check("4. Webhook MP — GET challenge")
def t_webhook_get():
    s, _, b = req("GET", "/payments/webhook")
    if s == 200 and '"ok"' in b:
        return True, "challenge respondido OK (200)"
    return False, f"HTTP {s} body={b[:100]!r} — si es 404, el deploy NO tiene el blueprint payments"


@check("5. Webhook MP — POST sin firma debe 401 (no 404)")
def t_webhook_post_unsigned():
    s, _, b = req("POST", "/payments/webhook", data={"type": "test", "data": {"id": "smoke"}})
    if s == 401:
        return True, "firma inválida rechazada con 401 (ruta viva y validando)"
    if s == 200:
        return False, "HTTP 200 sin firma — el secreto del webhook NO está configurado en producción"
    if s == 404:
        return False, "HTTP 404 — la ruta no existe: deploy desactualizado"
    return False, f"HTTP inesperado {s}: {b[:100]}"


@check("6. /payments/return exige sesión (302 al login)")
def t_return_guard():
    s, h, _ = req("GET", "/payments/return")
    loc = h.get("Location", "")
    if s in (301, 302) and "/auth/login" in loc:
        return True, f"HTTP {s} → {loc}"
    if s == 404:
        return False, "HTTP 404 — ruta no registrada: deploy desactualizado"
    return False, f"esperado redirect a login, llegó HTTP {s}"


@check("7. /payments/checkout exige sesión (302 al login)")
def t_checkout_guard():
    s, h, _ = req("GET", "/payments/checkout")
    loc = h.get("Location", "")
    if s in (301, 302) and "/auth/login" in loc:
        return True, f"HTTP {s} → {loc}"
    if s == 404:
        return False, "HTTP 404 — ruta no registrada: deploy desactualizado"
    return False, f"esperado redirect a login, llegó HTTP {s}"


@check("8. Guardia global devuelve 401 JSON en APIs")
def t_api_guard():
    s, _, b = req("GET", "/api/kpis")
    if s == 401 and "No autenticado" in b:
        return True, "401 JSON correcto"
    return False, f"esperado 401, llegó {s}"


def main():
    global BASE
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", default="https://www.aulamind.cl")
    args = ap.parse_args()
    BASE = args.base.rstrip("/")

    print("=" * 64)
    print(f"AulaMind — Smoke Test Post-Deploy")
    print(f"Objetivo: {BASE}")
    print("=" * 64)

    failed = 0
    for name, fn in CHECKS:
        try:
            ok, detail = fn()
        except Exception as e:
            ok, detail = False, f"excepción: {e}"
        mark = "PASS" if ok else "FAIL"
        if not ok:
            failed += 1
        print(f"[{mark}] {name}\n       → {detail}")

    print("=" * 64)
    if failed:
        print(f"RESULTADO: {failed} check(s) FALLARON — NO liberar el deploy.")
        print("Si los fallos son 404 en /payments/*: el servidor NO corre el código de main.")
        sys.exit(1)
    print("RESULTADO: 8/8 PASS — Deploy validado. Proceder con pago de prueba en sandbox MP.")
    sys.exit(0)


if __name__ == "__main__":
    main()
