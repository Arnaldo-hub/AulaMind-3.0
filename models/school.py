"""
===========================================================
AulaMind Enterprise 3.0
models/school.py
-----------------------------------------------------------

Modelo School

Compatible with:

✓ SQLite
✓ PostgreSQL
✓ SQLAlchemy 2.x

Author:
Biotecno Chile
===========================================================
"""

import uuid
from datetime import datetime

from sqlalchemy import Boolean
from sqlalchemy import DateTime
from sqlalchemy import Integer
from sqlalchemy import String

from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship

from database.base import Base


class School(Base):

    __tablename__ = "schools"

    # =====================================================
    # ID
    # =====================================================

    id: Mapped[str] = mapped_column(

        String(36),

        primary_key=True,

        default=lambda: str(uuid.uuid4())

    )

    # =====================================================
    # Información General
    # =====================================================

    name: Mapped[str] = mapped_column(

        String(200),

        nullable=False

    )

    rut: Mapped[str | None] = mapped_column(

        String(20),

        unique=True,

        nullable=True

    )

    email: Mapped[str | None] = mapped_column(

        String(255),

        nullable=True

    )

    phone: Mapped[str | None] = mapped_column(

        String(30),

        nullable=True

    )

    website: Mapped[str | None] = mapped_column(

        String(255),

        nullable=True

    )

    # =====================================================
    # Dirección
    # =====================================================

    address: Mapped[str | None] = mapped_column(

        String(255),

        nullable=True

    )

    city: Mapped[str | None] = mapped_column(

        String(100),

        nullable=True

    )

    region: Mapped[str | None] = mapped_column(

        String(100),

        nullable=True

    )

    country: Mapped[str] = mapped_column(

        String(100),

        default="Chile",

        nullable=False

    )

    # =====================================================
    # Información Académica
    # =====================================================

    dependency: Mapped[str | None] = mapped_column(

        String(100),

        nullable=True

    )

    levels: Mapped[str | None] = mapped_column(

        String(255),

        nullable=True

    )

    students: Mapped[int] = mapped_column(

        Integer,

        default=0,

        nullable=False

    )

    teachers: Mapped[int] = mapped_column(

        Integer,

        default=0,

        nullable=False

    )

    # =====================================================
    # Estado
    # =====================================================

    active: Mapped[bool] = mapped_column(

        Boolean,

        default=True,

        nullable=False

    )

    # =====================================================
    # Auditoría
    # =====================================================

    created_at: Mapped[datetime] = mapped_column(

        DateTime,

        default=datetime.utcnow,

        nullable=False

    )

    updated_at: Mapped[datetime] = mapped_column(

        DateTime,

        default=datetime.utcnow,

        onupdate=datetime.utcnow,

        nullable=False

    )

    # =====================================================
    # Relaciones
    # =====================================================

    users = relationship(

        "User",

        back_populates="school",

        cascade="all, delete-orphan"

    )

    subscription = relationship(
        "SchoolSubscription",
        back_populates="school",
        uselist=False
    )

    # =====================================================
    # Representación
    # =====================================================

    def __repr__(self):

        return f"<School({self.name})>"

    # =====================================================
    # Serialización
    # =====================================================

    def to_dict(self):

        return {

            "id": self.id,

            "name": self.name,

            "rut": self.rut,

            "email": self.email,

            "phone": self.phone,

            "website": self.website,

            "address": self.address,

            "city": self.city,

            "region": self.region,

            "country": self.country,

            "dependency": self.dependency,

            "levels": self.levels,

            "students": self.students,

            "teachers": self.teachers,

            "active": self.active,

            "created_at": self.created_at.isoformat()

            if self.created_at else None

        }