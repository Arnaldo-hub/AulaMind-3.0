"""
===========================================================
AulaMind Enterprise 3.0
database/base.py
-----------------------------------------------------------

Base Declarativa SQLAlchemy

Todas las entidades del sistema deberán heredar
desde esta clase.

===========================================================
"""

from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import MetaData


# ==========================================================
# Convenciones para nombres de índices y claves
# ==========================================================

convention = {

    "ix": "ix_%(column_0_label)s",

    "uq": "uq_%(table_name)s_%(column_0_name)s",

    "ck": "ck_%(table_name)s_%(constraint_name)s",

    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",

    "pk": "pk_%(table_name)s"

}


metadata = MetaData(

    naming_convention=convention

)


# ==========================================================
# Base
# ==========================================================

class Base(DeclarativeBase):

    metadata = metadata