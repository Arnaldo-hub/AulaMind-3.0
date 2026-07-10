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

    APP_VERSION = "3.0.0"

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
    SESSION_COOKIE_SECURE = os.getenv(
        "SESSION_COOKIE_SECURE", "False"
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
