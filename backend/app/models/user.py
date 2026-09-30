from __future__ import annotations

import enum
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Enum, Numeric, String, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class UserRole(str, enum.Enum):
    asesor = "asesor"
    cliente = "cliente"


class TipoIdentificacion(str, enum.Enum):
    CC = "CC"
    CE = "CE"
    PA = "PA"
    NIT = "NIT"


class TipoPrestamo(str, enum.Enum):
    hipotecario = "hipotecario"
    libranza = "libranza"
    libre_inversion = "libre_inversion"


class User(Base):
    __tablename__ = "users"
    __table_args__ = (
        UniqueConstraint(
            "tipo_identificacion",
            "numero_identificacion",
            name="uq_users_identificacion",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    nombre: Mapped[str] = mapped_column(String(120), nullable=False)
    tipo_identificacion: Mapped[TipoIdentificacion] = mapped_column(
        Enum(TipoIdentificacion, name="tipo_identificacion"),
        nullable=False,
    )
    numero_identificacion: Mapped[str] = mapped_column(String(40), nullable=False)
    correo: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    rol: Mapped[UserRole] = mapped_column(Enum(UserRole, name="user_role"), nullable=False)
    salario: Mapped[float | None] = mapped_column(Numeric(14, 2), nullable=True)
    tipo_prestamo: Mapped[TipoPrestamo | None] = mapped_column(
        Enum(TipoPrestamo, name="tipo_prestamo"),
        nullable=True,
    )
    monto_prestamo: Mapped[float | None] = mapped_column(Numeric(14, 2), nullable=True)
    activo: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True, server_default="true")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
