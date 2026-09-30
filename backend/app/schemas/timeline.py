from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.solicitud import SolicitudEstado
from app.schemas.invitations import SolicitudPublic


class TimelineEventPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    solicitud_id: int
    from_state: SolicitudEstado | None
    to_state: SolicitudEstado
    actor_id: int
    nota: str | None = None
    created_at: datetime


class TransitionRequest(BaseModel):
    nuevo_estado: SolicitudEstado
    nota: str | None = Field(default=None, max_length=280)


class SolicitudDetail(SolicitudPublic):
    timeline: list[TimelineEventPublic]
    transiciones_disponibles: list[SolicitudEstado] = []
