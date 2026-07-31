"""
===========================================================
AulaMind Enterprise 3.0
routes/legal.py

Páginas legales públicas (v3.1.4):
- Términos y Condiciones del Servicio
- Política de Privacidad y Tratamiento de Datos

Exigidas para operar comercialmente en Chile
(Ley 19.628 y Ley 21.719 de protección de datos
personales, esta última en vigencia desde dic-2026).
===========================================================
"""

from flask import Blueprint, render_template

legal = Blueprint("legal", __name__)


@legal.route("/terminos")
def terms():
    return render_template("legal_terms.html")


@legal.route("/privacidad")
def privacy():
    return render_template("legal_privacy.html")
