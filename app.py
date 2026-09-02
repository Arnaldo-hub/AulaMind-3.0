"""
===========================================================
AulaMind Enterprise 3.0
app.py
-----------------------------------------------------------

Punto de entrada principal

Autor:
Biotecno Chile
===========================================================
"""

from dotenv import load_dotenv
load_dotenv()

from flask import Flask, redirect, url_for, jsonify, request, session, render_template

from config import Config
from flask_wtf.csrf import CSRFProtect, CSRFError
from extensions import limiter
from routes.export import export
from routes.guides import guides  # ← NUEVO
from routes.rubrics import rubrics  # ← NUEVO
from routes.pie import pie  # ← NUEVO
from routes.fonoaudiologia import fonoaudiologia

# ==========================================================
# Base de datos
# ==========================================================


# ==========================================================
# IMPORTAR TODOS LOS MODELOS
# (Necesario para que SQLAlchemy registre el metadata completo)
# ==========================================================

from models.user import User
from models.school import School
from models.subscription import Subscription
from models.course import Course
from models.subject import Subject
from models.unit import Unit
from models.learning_objective import LearningObjective
from models.document import Document
from models.ai_generation import AIGeneration
from models.export import Export
from models.usage_event import UsageEvent
from models.user_subscription import UserSubscription  # ← NUEVO v3.1
from models.school_subscription import SchoolSubscription  # ← NUEVO v3.3 Plan Institucional
from database.session import create_database

# ==========================================================
# IMPORTAR BLUEPRINTS
# ==========================================================

from routes.dashboard import dashboard
from routes.auth import auth
from routes.planning import planning
from routes.curriculum import curriculum
from routes.curriculum_api import curriculum_api
from routes.curriculum_api_v4 import curriculum_api_v4
from routes.evaluation import evaluation
from routes.admin_security import admin_security
from routes.password_reset import password_reset
from routes.analytics import analytics  # ← NUEVO
from routes.billing import billing  # ← NUEVO v3.1
from routes.legal import legal  # ← NUEVO v3.1.4 páginas legales
from routes.payments import payments  # ← NUEVO v3.2 Mercado Pago
from routes.admin_comercial import admin_comercial  # ← NUEVO v3.3 Panel Comercial

# ==========================================================
# CREAR APP
# ==========================================================

app = Flask(__name__)

app.config.from_object(Config)

app.secret_key = Config.SECRET_KEY

csrf = CSRFProtect(app)
limiter.init_app(app)

@app.errorhandler(CSRFError)
def handle_csrf_error(error):
    return jsonify({
        "error": "csrf_invalid",
        "message": "La solicitud expiró o no es válida. Recarga la página e inténtalo nuevamente."
    }), 400

# ==========================================================
# REGISTRAR BLUEPRINTS
# ==========================================================

app.register_blueprint(
    dashboard
)

app.register_blueprint(
    auth,
    url_prefix="/auth"
)

app.register_blueprint(planning)
app.register_blueprint(curriculum)
app.register_blueprint(curriculum_api)
app.register_blueprint(curriculum_api_v4)
app.register_blueprint(evaluation)
app.register_blueprint(admin_security)
app.register_blueprint(admin_comercial)  # ← NUEVO v3.3 Panel Comercial
app.register_blueprint(password_reset, url_prefix="/auth")
app.register_blueprint(export)
app.register_blueprint(analytics)  # ← NUEVO
app.register_blueprint(guides)  # ← NUEVO
app.register_blueprint(rubrics)  # ← NUEVO
app.register_blueprint(pie)  # ← NUEVO
app.register_blueprint(billing)  # ← NUEVO v3.1
app.register_blueprint(legal)  # ← NUEVO v3.1.4
app.register_blueprint(payments)  # ← NUEVO v3.2 Mercado Pago

# El webhook de Mercado Pago es un POST server-to-server:
# no lleva token CSRF de sesión. Se exime SOLO este
# blueprint (sus otras rutas son GET de todos modos).
csrf.exempt(payments)

# ==========================================================
# TABLAS: crear las que falten al arrancar (v3.1)
# create_all es idempotente: no toca tablas existentes.
# Se envuelve en try/except para no tumbar el boot si la
# BD aún no está disponible (primer deploy, cold start).
# ==========================================================

try:
    create_database()
except Exception as e:
    print(f"[boot] create_database omitido: {e}")

# ==========================================================
# RUTA RAÍZ
# ==========================================================

@app.route("/")
def index():

    # v3.1: la raíz muestra la landing pública; con sesión
    # activa va directo al dashboard.
    if session.get("user_id"):
        return redirect(url_for("dashboard.home"))

    return render_template("landing.html")

# ==========================================================
# STATUS
# ==========================================================

@app.route("/health")
def health():
    return {"status": "ok", "application": Config.APP_NAME, "version": Config.APP_VERSION}

@app.route("/status")
def status():

    return {

        "application": Config.APP_NAME,
        "version": Config.APP_VERSION,
        "database": "configured",
        "status": "running"

    }

# ==========================================================
# GUARDIA GLOBAL DE AUTENTICACIÓN
# Toda la plataforma exige sesión activa, salvo los
# endpoints públicos listados abajo. (DT-016)
# ==========================================================

PUBLIC_ENDPOINTS = {
    "index",
    "health",
    "dashboard.health",  # colisión: dashboard.py también define /health y gana por orden de registro
    "status",
    "static",
    "auth.login",
    "auth.register",
    "password_reset.forgot_password",
    "password_reset.reset_password",
    "legal.terms",
    "legal.privacy",
    "payments.webhook",
}


@app.before_request
def require_login_globally():

    endpoint = request.endpoint

    if endpoint is None or endpoint in PUBLIC_ENDPOINTS:
        return None

    if session.get("user_id"):
        return None

    # APIs responden 401 JSON; páginas redirigen al login
    if "/api/" in request.path:
        return jsonify({"error": "No autenticado"}), 401

    return redirect(url_for("auth.login"))


# ==========================================================
# MAIN
# ==========================================================

if __name__ == "__main__":

    print("=" * 60)
    print("AulaMind Enterprise 3.0")
    print("=" * 60)
    print(f"Aplicación : {Config.APP_NAME}")
    print(f"Versión    : {Config.APP_VERSION}")
    print(f"Base Datos : {Config.SQLALCHEMY_DATABASE_URI}")
    print("=" * 60)

    app.run(

        host="127.0.0.1",

        port=5000,

        debug=Config.DEBUG

    )
