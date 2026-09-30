from __future__ import annotations

import enum
from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.user import TipoIdentificacion


class SolicitudEstado(str, enum.Enum):
    recibido = "recibido"
    en_estudio = "en_estudio"
    aprobado = "aprobado"
    rechazado = "rechazado"


class InvitacionEstado(str, enum.Enum):
    pendiente = "pendiente"
    vinculada = "vinculada"


class Solicitud(Base):
    __tablename__ = "solicitudes"

    id: Mapped[int] = mapped_column(primary_key=True)
    asesor_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    cliente_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id"),
        nullable=True,
        index=True,
    )
    estado: Mapped[SolicitudEstado] = mapped_column(
        Enum(SolicitudEstado, name="solicitud_estado"),
        nullable=False,
        default=SolicitudEstado.recibido,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    invitacion: Mapped[Invitacion | None] = relationship(
        back_populates="solicitud",
        uselist=False,
    )


class Invitacion(Base):
    __tablename__ = "invitaciones"

    id: Mapped[int] = mapped_column(primary_key=True)
    asesor_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    solicitud_id: Mapped[int] = mapped_column(
        ForeignKey("solicitudes.id"),
        nullable=False,
        unique=True,
    )
    correo_objetivo: Mapped[str | None] = mapped_column(String(255), nullable=True, index=True)
    tipo_identificacion: Mapped[TipoIdentificacion | None] = mapped_column(
        Enum(TipoIdentificacion, name="tipo_identificacion", create_constraint=False),
        nullable=True,
    )
    numero_identificacion: Mapped[str | None] = mapped_column(String(40), nullable=True)
    estado: Mapped[InvitacionEstado] = mapped_column(
        Enum(InvitacionEstado, name="invitacion_estado"),
        nullable=False,
        default=InvitacionEstado.pendiente,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    solicitud: Mapped[Solicitud] = relationship(back_populates="invitacion")
