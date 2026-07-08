"""
===========================================================
AulaMind Enterprise 3.0
database/session.py
-----------------------------------------------------------

Gestión de la conexión a la base de datos.

Características:

✓ SQLite para desarrollo local.
✓ PostgreSQL para producción (Render).
✓ SQLAlchemy 2.x.
✓ Session Factory.
✓ Gestión de sesiones.
✓ Creación automática de tablas.

Autor:
Biotecno Chile
===========================================================
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from config import Config
from database.base import Base


# ==========================================================
# Engine
# ==========================================================

engine = create_engine(

    Config.SQLALCHEMY_DATABASE_URI,

    future=True,

    echo=False,

    pool_pre_ping=True

)


# ==========================================================
# Session Factory
# ==========================================================

SessionLocal = sessionmaker(

    bind=engine,

    autoflush=False,

    autocommit=False,

    expire_on_commit=False

)


# ==========================================================
# Obtener sesión
# ==========================================================

def get_db():
    """
    Dependencia para obtener una sesión.

    Uso:

        for db in get_db():
            ...

    """

    db = SessionLocal()

    try:

        yield db

    finally:

        db.close()


# ==========================================================
# Crear todas las tablas
# ==========================================================

def create_database():

    Base.metadata.create_all(

        bind=engine

    )


# ==========================================================
# Probar conexión
# ==========================================================

def test_connection():

    try:

        with engine.connect():

            return True

    except Exception as e:

        print(f"[DATABASE ERROR] {e}")

        return False


# ==========================================================
# Información de la Base de Datos
# ==========================================================

def database_info():

    return {

        "database_uri": Config.SQLALCHEMY_DATABASE_URI,

        "engine": str(engine.url),

        "connected": test_connection()

    }