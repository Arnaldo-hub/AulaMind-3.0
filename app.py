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

from flask import Flask, redirect, url_for, jsonify

from config import Config
from flask_wtf.csrf import CSRFProtect, CSRFError
from extensions import limiter

# ==========================================================
# Base de datos
# ==========================================================


# ==========================================================
# IMPORTAR TODOS LOS MODELOS
# (Necesario para que SQLAlchemy cree las tablas)
# ==========================================================

from models.user import User
from models.school import School
from models.subscription import Subscription
from models.document import Document
from models.ai_generation import AIGeneration
from models.export import Export
from models.usage_event import UsageEvent

# ==========================================================
# IMPORTAR BLUEPRINTS
# ==========================================================

from routes.dashboard import dashboard
from routes.auth import auth
from routes.planning import planning
from routes.curriculum import curriculum
from routes.curriculum_api import curriculum_api
from routes.evaluation import evaluation
from routes.admin_security import admin_security
from routes.password_reset import password_reset

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

app.register_blueprint(
    planning
)

app.register_blueprint(curriculum)
app.register_blueprint(curriculum_api)
app.register_blueprint(evaluation)
app.register_blueprint(admin_security)
app.register_blueprint(password_reset, url_prefix="/auth")

# ==========================================================
# RUTA RAÍZ
# ==========================================================

@app.route("/")
def index():

    return redirect(
        url_for("dashboard.home")
    )

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
