"""
===========================================================
AulaMind Enterprise 3.0
routes/analytics.py
-----------------------------------------------------------

Módulo de Analítica y Dashboard Curricular

Consume:
    - api.providers.dashboard_provider
    - services.dashboard.models

Autor:
Biotecno Chile
===========================================================
"""

from flask import (
    Blueprint,
    render_template,
    jsonify,
    session,
    redirect,
    url_for,
    current_app
)

from api.providers.dashboard_provider import dashboard_provider

# ==========================================================
# BLUEPRINT
# ==========================================================

analytics = Blueprint(
    "analytics",
    __name__,
    url_prefix="/analytics"
)

# ==========================================================
# UTILIDADES
# ==========================================================

def _to_dict(obj):
    """
    Convierte dataclasses, listas y tuplas a dict/list serializables.
    """
    from dataclasses import asdict, is_dataclass

    if is_dataclass(obj):
        return asdict(obj)
    if isinstance(obj, list):
        return [_to_dict(item) for item in obj]
    if isinstance(obj, tuple):
        return list(obj)
    return obj

# ==========================================================
# PÁGINA PRINCIPAL
# ==========================================================

@analytics.route("/")
def index():
    """
    Dashboard analítico completo.
    """

    if "user_id" not in session:
        return redirect(url_for("auth.login"))

    try:
        report = dashboard_provider.build()
    except Exception as exc:
        current_app.logger.exception("Error generando DashboardReport")
        report = None

    return render_template(
        "analytics.html",
        title="Analítica",
        user_name=session.get("user_name", "Profesor"),
        report=report
    )

# ==========================================================
# API JSON — KPIs
# ==========================================================

@analytics.route("/api/kpis")
def api_kpis():

    if "user_id" not in session:
        return jsonify(success=False, error="No autenticado"), 401

    try:
        kpis = dashboard_provider.kpis()
        return jsonify(success=True, kpis=_to_dict(kpis))
    except Exception as exc:
        current_app.logger.exception("Error KPIs")
        return jsonify(success=False, error=str(exc)), 500

# ==========================================================
# API JSON — Alertas
# ==========================================================

@analytics.route("/api/alerts")
def api_alerts():

    if "user_id" not in session:
        return jsonify(success=False, error="No autenticado"), 401

    try:
        alerts = dashboard_provider.alerts()
        return jsonify(success=True, alerts=_to_dict(alerts))
    except Exception as exc:
        current_app.logger.exception("Error Alertas")
        return jsonify(success=False, error=str(exc)), 500

# ==========================================================
# API JSON — Gráficos
# ==========================================================

@analytics.route("/api/charts")
def api_charts():

    if "user_id" not in session:
        return jsonify(success=False, error="No autenticado"), 401

    try:
        charts = dashboard_provider.charts()
        return jsonify(success=True, charts=_to_dict(charts))
    except Exception as exc:
        current_app.logger.exception("Error Charts")
        return jsonify(success=False, error=str(exc)), 500

# ==========================================================
# API JSON — Rankings
# ==========================================================

@analytics.route("/api/rankings")
def api_rankings():

    if "user_id" not in session:
        return jsonify(success=False, error="No autenticado"), 401

    try:
        rankings = dashboard_provider.rankings()
        return jsonify(success=True, rankings=_to_dict(rankings))
    except Exception as exc:
        current_app.logger.exception("Error Rankings")
        return jsonify(success=False, error=str(exc)), 500

# ==========================================================
# HEALTH
# ==========================================================

@analytics.route("/health")
def health():

    return jsonify(
        module="Analytics",
        status="running",
        version="1.0"
    )