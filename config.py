"""
===========================================================
AulaMind Enterprise 3.0
config.py
-----------------------------------------------------------

Configuración centralizada de AulaMind.

Modo Desarrollo
---------------
SQLite

Modo Producción
---------------
PostgreSQL (Render)

Nunca modificar este archivo para cambiar
entre desarrollo y producción.

===========================================================
"""

import os
from pathlib import Path
from dotenv import load_dotenv


class Config:
    """
    Configuración principal de AulaMind.
    """

    # =====================================================
    # Directorio Base
    # =====================================================

    BASE_DIR = Path(__file__).resolve().parent

    # =====================================================
    # Aplicación
    # =====================================================

    APP_NAME = "AulaMind Enterprise"

    APP_VERSION = "3.3.2"

    COMPANY = "Biotecno Chile"

    COUNTRY = "Chile"

    DEFAULT_LANGUAGE = "es"

    TIMEZONE = "America/Santiago"

    # =====================================================
    # Flask
    # =====================================================

    SECRET_KEY = os.getenv("SECRET_KEY")

    if not SECRET_KEY:
        if os.getenv("DEBUG", "True").lower() == "true":
            SECRET_KEY = "AulaMind-Local-Development-Only"
        else:
            raise RuntimeError("SECRET_KEY es obligatoria fuera de desarrollo.")

    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    # Secure por defecto: solo se desactiva en desarrollo local
    # explícito (DEBUG=true). En producción la cookie de sesión
    # viaja únicamente por HTTPS.
    SESSION_COOKIE_SECURE = os.getenv(
        "SESSION_COOKIE_SECURE",
        "false" if os.getenv("DEBUG", "True").lower() == "true" else "true"
    ).lower() == "true"
    PERMANENT_SESSION_LIFETIME = 60 * 60 * 8

    DEBUG = os.getenv(

        "DEBUG",

        "True"

    ).lower() == "true"

    JSON_SORT_KEYS = False

    TEMPLATES_AUTO_RELOAD = True

    MAX_CONTENT_LENGTH = 20 * 1024 * 1024

    # =====================================================
    # Rate limiting
    # =====================================================

    # Desarrollo:
    #     memory://
    #
    # Producción:
    #     Redis si existe
    #     En caso contrario utiliza memoria para permitir
    #     que la aplicación arranque.

    RATELIMIT_STORAGE_URI = os.getenv("RATELIMIT_STORAGE_URI")

    if not RATELIMIT_STORAGE_URI:
        RATELIMIT_STORAGE_URI = "memory://"
        
    # =====================================================
    # Recuperación de contraseña
    # =====================================================

    PASSWORD_RESET_TOKEN_MAX_AGE = int(os.getenv("PASSWORD_RESET_TOKEN_MAX_AGE", "1800"))
    MAIL_SERVER = os.getenv("MAIL_SERVER", "")
    MAIL_PORT = int(os.getenv("MAIL_PORT", "587"))
    MAIL_USE_TLS = os.getenv("MAIL_USE_TLS", "True").lower() == "true"
    MAIL_USE_SSL = os.getenv("MAIL_USE_SSL", "False").lower() == "true"
    MAIL_USERNAME = os.getenv("MAIL_USERNAME", "")
    MAIL_PASSWORD = os.getenv("MAIL_PASSWORD", "")
    MAIL_FROM = os.getenv("MAIL_FROM", MAIL_USERNAME or "no-reply@aulamind.local")

    if MAIL_USE_TLS and MAIL_USE_SSL:
        raise RuntimeError("MAIL_USE_TLS y MAIL_USE_SSL no pueden estar activos simultáneamente.")

    # =====================================================
    # Trial Comercial (v3.1)
    # =====================================================

    TRIAL_DAYS = int(os.getenv("TRIAL_DAYS", "3"))

    TRIAL_MAX_GENERATIONS = int(os.getenv("TRIAL_MAX_GENERATIONS", "10"))

    TRIAL_PLAN_NAME = os.getenv("TRIAL_PLAN_NAME", "Trial")

    PRO_PLAN_NAME = os.getenv("PRO_PLAN_NAME", "Pro")

    PRO_MONTHLY_PRICE_CLP = int(os.getenv("PRO_MONTHLY_PRICE_CLP", "9990"))

    # WhatsApp comercial (botón "Activar Plan Pro" en Mi Plan).
    # Solo dígitos, con código de país, sin '+'.
    WHATSAPP_NUMBER = os.getenv("WHATSAPP_NUMBER", "56954690241")

    # =====================================================
    # Mercado Pago — Suscripciones (v3.2)
    # Credenciales de PRODUCCIÓN de la aplicación
    # "AulaMind" (panel Developers de MP). El Access Token
    # NUNCA va al frontend: solo vive en variables de
    # entorno del servidor.
    # MERCADOPAGO_WEBHOOK_SECRET: firma secreta que MP
    # muestra al configurar la URL del webhook; si está
    # vacío, el webhook valida solo por consulta a la API.
    # =====================================================

    MERCADOPAGO_ACCESS_TOKEN = os.getenv(
        "MERCADOPAGO_ACCESS_TOKEN", ""
    )

    MERCADOPAGO_PUBLIC_KEY = os.getenv(
        "MERCADOPAGO_PUBLIC_KEY", ""
    )

    MERCADOPAGO_WEBHOOK_SECRET = os.getenv(
        "MERCADOPAGO_WEBHOOK_SECRET", ""
    )

    MERCADOPAGO_SUCCESS_URL = os.getenv(
        "MERCADOPAGO_SUCCESS_URL",
        "https://www.aulamind.cl/payments/return"
    )

    # =====================================================
    # Base de Datos
    # =====================================================

    DATABASE_URL = os.getenv("DATABASE_URL")

    if DATABASE_URL:

        # Render / PostgreSQL

        SQLALCHEMY_DATABASE_URI = DATABASE_URL

    else:

        # Desarrollo Local (SQLite)

        SQLALCHEMY_DATABASE_URI = (

            "sqlite:///" +

            str(BASE_DIR / "aulamind.db")

        )

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # =====================================================
    # OpenAI
    # =====================================================

    OPENAI_API_KEY = os.getenv(

        "OPENAI_API_KEY",

        ""

    )

    OPENAI_MODEL = os.getenv(

        "OPENAI_MODEL",

        "gpt-4.1"

    )

    # =====================================================
    # Hugging Face
    # =====================================================

    HF_TOKEN = os.getenv(

        "HF_TOKEN",

        ""

    )

    # =====================================================
    # Exportaciones
    # =====================================================

    EXPORT_FOLDER = BASE_DIR / "exports"

    EXPORT_FOLDER.mkdir(

        exist_ok=True

    )

    # =====================================================
    # Currículum
    # =====================================================

    CURRICULUM_FOLDER = BASE_DIR / "data_curricular"

    CURRICULUM_FOLDER.mkdir(

        exist_ok=True

    )

    # =====================================================
    # Logs
    # =====================================================

    LOG_LEVEL = os.getenv(

        "LOG_LEVEL",

        "INFO"

    )

    LOG_FOLDER = BASE_DIR / "logs"

    LOG_FOLDER.mkdir(

        exist_ok=True

    )
