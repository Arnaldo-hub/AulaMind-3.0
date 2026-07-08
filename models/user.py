"""
===========================================================
AulaMind Enterprise 3.0
models/user.py
-----------------------------------------------------------

Modelo Usuario

Compatible con:

✓ SQLite
✓ PostgreSQL
✓ SQLAlchemy 2.x

===========================================================
"""

import uuid
from datetime import datetime

from sqlalchemy import String
from sqlalchemy import Boolean
from sqlalchemy import DateTime
from sqlalchemy import ForeignKey

from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship

from database.base import Base


class User(Base):

    __tablename__ = "users"

    # ======================================================
    # Identificador
    # ======================================================

    id: Mapped[str] = mapped_column(

        String(36),

        primary_key=True,

        default=lambda: str(uuid.uuid4())

    )

    # ======================================================
    # Información Personal
    # ======================================================

    first_name: Mapped[str] = mapped_column(

        String(100),

        nullable=False

    )

    last_name: Mapped[str] = mapped_column(

        String(100),

        nullable=False

    )

    email: Mapped[str] = mapped_column(

        String(255),

        nullable=False,

        unique=True,

        index=True

    )

    phone: Mapped[str | None] = mapped_column(

        String(30),

        nullable=True

    )

    # ======================================================
    # Seguridad
    # ======================================================

    password_hash: Mapped[str] = mapped_column(

        String(255),

        nullable=False

    )

    is_active: Mapped[bool] = mapped_column(

        Boolean,

        default=True,

        nullable=False

    )

    is_admin: Mapped[bool] = mapped_column(

        Boolean,

        default=False,

        nullable=False

    )

    email_verified: Mapped[bool] = mapped_column(

        Boolean,

        default=False,

        nullable=False

    )

    # ======================================================
    # Perfil
    # ======================================================

    avatar: Mapped[str | None] = mapped_column(

        String(255),

        nullable=True

    )

    language: Mapped[str] = mapped_column(

        String(20),

        default="es"

    )

    timezone: Mapped[str] = mapped_column(

        String(60),

        default="America/Santiago"

    )

    country: Mapped[str] = mapped_column(

        String(100),

        default="Chile"

    )

    city: Mapped[str | None] = mapped_column(

        String(100),

        nullable=True

    )

    # ======================================================
    # Relaciones
    # ======================================================

    school_id: Mapped[str | None] = mapped_column(

        String(36),

        ForeignKey("schools.id"),

        nullable=True

    )

    subscription_id: Mapped[str | None] = mapped_column(

        String(36),

        ForeignKey("subscriptions.id"),

        nullable=True

    )

    school = relationship(

        "School",

        back_populates="users"

    )

    subscription = relationship(

        "Subscription",

        back_populates="users"

    )

    # ======================================================
    # Auditoría
    # ======================================================

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

    last_login: Mapped[datetime | None] = mapped_column(

        DateTime,

        nullable=True

    )

    # ======================================================
    # Representación
    # ======================================================

    def __repr__(self):

        return (

            f"<User("

            f"{self.email}"

            f")>"

        )

    # ======================================================
    # Nombre Completo
    # ======================================================

    @property
    def full_name(self):

        return f"{self.first_name} {self.last_name}"

    # ======================================================
    # Serialización
    # ======================================================

    def to_dict(self):

        return {

            "id": self.id,

            "first_name": self.first_name,

            "last_name": self.last_name,

            "full_name": self.full_name,

            "email": self.email,

            "phone": self.phone,

            "country": self.country,

            "city": self.city,

            "language": self.language,

            "timezone": self.timezone,

            "is_active": self.is_active,

            "is_admin": self.is_admin,

            "email_verified": self.email_verified,

            "created_at": self.created_at.isoformat()

            if self.created_at else None

        }