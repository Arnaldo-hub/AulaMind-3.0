"""
===========================================================
AulaMind Enterprise 3.0
models/course.py
-----------------------------------------------------------
Modelo Course

Representa un curso del sistema educativo chileno.

Ejemplos:
- Pre-Kínder
- Kínder
- 1° Básico
- 2° Básico
...
- IV Medio

Autor: Biotecno Chile
===========================================================
"""

from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    DateTime,
    func
)
from sqlalchemy.orm import relationship

from database.base import Base


class Course(Base):
    """
    Modelo de Cursos.
    """

    __tablename__ = "courses"

    # =====================================================
    # CAMPOS
    # =====================================================

    id = Column(
        Integer,
        primary_key=True,
        autoincrement=True
    )

    name = Column(
        String(100),
        nullable=False,
        unique=True,
        index=True
    )

    short_name = Column(
        String(20),
        nullable=False,
        unique=True
    )

    level = Column(
        String(50),
        nullable=False,
        index=True
    )

    order = Column(
        Integer,
        nullable=False,
        default=0
    )

    is_active = Column(
        Boolean,
        default=True,
        nullable=False
    )

    created_at = Column(
        DateTime,
        server_default=func.now()
    )

    updated_at = Column(
        DateTime,
        server_default=func.now(),
        onupdate=func.now()
    )

    # =====================================================
    # RELACIONES
    # =====================================================

    subjects = relationship(
        "Subject",
        back_populates="course",
        cascade="all, delete-orphan",
        lazy="select"
    )

    units = relationship(
        "Unit",
        back_populates="course",
        cascade="all, delete-orphan",
        lazy="select"
    )

    learning_objectives = relationship(
        "LearningObjective",
        back_populates="course",
        cascade="all, delete-orphan",
        lazy="select"
    )

    # =====================================================
    # MÉTODOS
    # =====================================================

    def to_dict(self):
        """
        Convierte el modelo en un diccionario.
        """

        return {

            "id": self.id,

            "name": self.name,

            "short_name": self.short_name,

            "level": self.level,

            "order": self.order,

            "is_active": self.is_active

        }

    def __repr__(self):

        return (

            f"<Course("
            f"id={self.id}, "
            f"name='{self.name}', "
            f"level='{self.level}'"
            f")>"

        )