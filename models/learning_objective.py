"""
===========================================================
AulaMind Enterprise 3.0
models/learning_objective.py
-----------------------------------------------------------

Modelo LearningObjective

Representa un Objetivo de Aprendizaje (OA)
del Currículum Nacional de Chile.

Este modelo será utilizado por:

• Planning Engine
• Evaluation Engine
• Guide Engine
• Rubric Engine
• PIE Engine
• Analytics Engine

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


class LearningObjective(Base):

    __tablename__ = "learning_objectives"

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

    unit_id = Column(
        Integer,
        ForeignKey("units.id"),
        nullable=False,
        index=True
    )

    code = Column(
        String(20),
        nullable=False,
        index=True
    )

    title = Column(
        String(300),
        nullable=False
    )

    description = Column(
        Text,
        nullable=False
    )

    indicators = Column(
        Text,
        nullable=True
    )

    skills = Column(
        Text,
        nullable=True
    )

    attitudes = Column(
        Text,
        nullable=True
    )

    evaluation_suggestions = Column(
        Text,
        nullable=True
    )

    minimum_classes = Column(
        Integer,
        default=1
    )

    estimated_hours = Column(
        Integer,
        default=6
    )

    bloom_level = Column(
        String(60),
        nullable=True
    )

    priority = Column(
        Integer,
        default=1
    )

    is_transversal = Column(
        Boolean,
        default=False
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
        back_populates="learning_objectives"
    )

    subject = relationship(
        "Subject",
        back_populates="learning_objectives"
    )

    unit = relationship(
        "Unit",
        back_populates="learning_objectives"
    )

    # =====================================================
    # PROPIEDADES
    # =====================================================

    @property
    def full_code(self):

        return f"{self.subject.short_name}-{self.code}"

    @property
    def short_description(self):

        if len(self.description) <= 120:
            return self.description

        return self.description[:120] + "..."

    # =====================================================
    # SERIALIZACIÓN
    # =====================================================

    def to_dict(self):

        return {

            "id": self.id,

            "course_id": self.course_id,

            "subject_id": self.subject_id,

            "unit_id": self.unit_id,

            "course": self.course.name if self.course else None,

            "subject": self.subject.name if self.subject else None,

            "unit": self.unit.title if self.unit else None,

            "code": self.code,

            "title": self.title,

            "description": self.description,

            "indicators": self.indicators,

            "skills": self.skills,

            "attitudes": self.attitudes,

            "evaluation_suggestions": self.evaluation_suggestions,

            "minimum_classes": self.minimum_classes,

            "estimated_hours": self.estimated_hours,

            "bloom_level": self.bloom_level,

            "priority": self.priority,

            "is_transversal": self.is_transversal,

            "is_active": self.is_active

        }

    # =====================================================
    # REPRESENTACIÓN
    # =====================================================

    def __repr__(self):

        return (

            f"<LearningObjective("

            f"id={self.id}, "

            f"code='{self.code}', "

            f"title='{self.title}'"

            f")>"

        )