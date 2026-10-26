"""
===========================================================
AulaMind Enterprise 3.0
routes/ayuda.py
-----------------------------------------------------------

Centro de Ayuda (v3.10.1): guia de uso dentro de la app.

Rutas:
  GET /ayuda         -> pagina de ayuda (requiere sesion)
  GET /ayuda/health -> estado del modulo

Autor:
Biotecno Chile
===========================================================
"""

import logging

from flask import Blueprint, jsonify, redirect, render_template, session

logger = logging.getLogger(__name__)

ayuda = Blueprint("ayuda", __name__, url_prefix="/ayuda")


@ayuda.route("/")
def index():
    if "user_id" not in session:
        return redirect("/auth/login")
    return render_template("ayuda.html")


@ayuda.route("/health")
def health():
    return jsonify(status="ok", service="ayuda", version="3.10.1")
