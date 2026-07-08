"""
===========================================================
AulaMind Enterprise 3.0
models/unit.py
-----------------------------------------------------------
Modelo Unit

Representa una Unidad de Aprendizaje del Currículum
Nacional de Chile.

Ejemplos:

Unidad 1
Unidad 2
Unidad 3
Unidad 4

Autor:
Biotecno Chile
===========================================================
"""

from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    Boolean,
    DateTime,
    ForeignKey,
    func
)

from sqlalchemy.orm import relationship

from database.base import Base


class Unit(Base):

    __tablename__ = "units"

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

    subject_id = Column(
        Integer,
        ForeignKey("subjects.id"),
        nullable=False,
        index=True
    )

    number = Column(
        Integer,
        nullable=False
    )

    title = Column(
        String(250),
        nullable=False
    )

    description = Column(
        Text,
        nullable=True
    )

    semester = Column(
        Integer,
        nullable=False,
        default=1
    )

    estimated_weeks = Column(
        Integer,
        nullable=False,
        default=4
    )

    estimated_hours = Column(
        Integer,
        nullable=False,
        default=24
    )

    color = Column(
        String(20),
        default="#2563EB"
    )

    icon = Column(
        String(60),
        default="fa-layer-group"
    )

    order = Column(
        Integer,
        default=1
    )

    is_active = Column(
        Boolean,
        nullable=False,
        default=True
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
        back_populates="units"
    )

    subject = relationship(
        "Subject",
        back_populates="units"
    )

    learning_objectives = relationship(
        "LearningObjective",
        back_populates="unit",
        cascade="all, delete-orphan",
        lazy="select"
    )

    # =====================================================
    # PROPIEDADES
    # =====================================================

    @property
    def full_name(self):

        return f"Unidad {self.number} - {self.title}"

    # =====================================================
    # SERIALIZACIÓN
    # =====================================================

    def to_dict(self):

        return {

            "id": self.id,

            "course_id": self.course_id,

            "subject_id": self.subject_id,

            "course": self.course.name if self.course else None,

            "subject": self.subject.name if self.subject else None,

            "number": self.number,

            "title": self.title,

            "description": self.description,

            "semester": self.semester,

            "estimated_weeks": self.estimated_weeks,

            "estimated_hours": self.estimated_hours,

            "color": self.color,

            "icon": self.icon,

            "order": self.order,

            "is_active": self.is_active

        }

    # =====================================================
    # REPRESENTACIÓN
    # =====================================================

    def __repr__(self):

        return (

            f"<Unit("

            f"id={self.id}, "

            f"number={self.number}, "

            f"title='{self.title}', "

            f"subject='{self.subject.name if self.subject else ''}'"

            f")>"

        )