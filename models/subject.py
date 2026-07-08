"""
===========================================================
AulaMind Enterprise 3.0
models/subject.py
-----------------------------------------------------------
Modelo Subject

Representa una asignatura del Currículum Nacional.

Ejemplos:

- Matemática
- Lenguaje y Comunicación
- Ciencias Naturales
- Historia
- Inglés
- Tecnología
- Música
- Artes Visuales
- Educación Física
- Filosofía
- Ciencias para la Ciudadanía

Autor:
Biotecno Chile
===========================================================
"""

from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    DateTime,
    ForeignKey,
    Text,
    func
)

from sqlalchemy.orm import relationship

from database.base import Base


class Subject(Base):

    """
    Modelo de Asignaturas.
    """

    __tablename__ = "subjects"

    # =====================================================
    # CAMPOS
    # =====================================================

    id = Column(
        Integer,
        primary_key=True,
        autoincrement=True
    )

    course_id = Column(
        Integer,
        ForeignKey("courses.id"),
        nullable=False,
        index=True
    )

    name = Column(
        String(120),
        nullable=False,
        index=True
    )

    short_name = Column(
        String(40),
        nullable=False
    )

    code = Column(
        String(20),
        nullable=True,
        unique=True
    )

    description = Column(
        Text,
        nullable=True
    )

    color = Column(
        String(20),
        default="#2563EB"
    )

    icon = Column(
        String(60),
        default="fa-book-open"
    )

    hours_per_week = Column(
        Integer,
        default=0
    )

    order = Column(
        Integer,
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

    course = relationship(
        "Course",
        back_populates="subjects"
    )

    units = relationship(
        "Unit",
        back_populates="subject",
        cascade="all, delete-orphan",
        lazy="select"
    )

    learning_objectives = relationship(
        "LearningObjective",
        back_populates="subject",
        cascade="all, delete-orphan",
        lazy="select"
    )

    # =====================================================
    # MÉTODOS
    # =====================================================

    @property
    def full_name(self):

        return f"{self.course.name} - {self.name}"

    def to_dict(self):

        return {

            "id": self.id,

            "course_id": self.course_id,

            "course": self.course.name if self.course else None,

            "name": self.name,

            "short_name": self.short_name,

            "code": self.code,

            "description": self.description,

            "color": self.color,

            "icon": self.icon,

            "hours_per_week": self.hours_per_week,

            "order": self.order,

            "is_active": self.is_active

        }

    def __repr__(self):

        return (

            f"<Subject("

            f"id={self.id}, "

            f"name='{self.name}', "

            f"course='{self.course.name if self.course else ''}'"

            f")>"

        )