from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.solicitud import SolicitudEstado


class TimelineEvent(Base):
    __tablename__ = "timeline_events"

    id: Mapped[int] = mapped_column(primary_key=True)
    solicitud_id: Mapped[int] = mapped_column(
        ForeignKey("solicitudes.id"),
        nullable=False,
        index=True,
    )
    from_state: Mapped[SolicitudEstado | None] = mapped_column(
        Enum(SolicitudEstado, name="solicitud_estado", create_constraint=False),
        nullable=True,
    )
    to_state: Mapped[SolicitudEstado] = mapped_column(
        Enum(SolicitudEstado, name="solicitud_estado", create_constraint=False),
        nullable=False,
    )
    actor_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    nota: Mapped[str | None] = mapped_column(String(280), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    solicitud = relationship("Solicitud", back_populates="timeline_events")
