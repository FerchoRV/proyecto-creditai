from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field, model_validator

from app.models.solicitud import InvitacionEstado, SolicitudEstado
from app.models.user import TipoIdentificacion


class InvitationCreateRequest(BaseModel):
    correo: EmailStr | None = None
    tipo_identificacion: TipoIdentificacion | None = None
    numero_identificacion: str | None = Field(default=None, min_length=3, max_length=40)

    @model_validator(mode="after")
    def require_target(self) -> InvitationCreateRequest:
        has_email = self.correo is not None
        has_id = (
            self.tipo_identificacion is not None
            and self.numero_identificacion is not None
            and self.numero_identificacion.strip() != ""
        )
        if not has_email and not has_id:
            raise ValueError(
                "Debes indicar correo y/o tipo+número de identificación del cliente"
            )
        if self.numero_identificacion is not None:
            self.numero_identificacion = self.numero_identificacion.strip()
        return self


class SolicitudPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    asesor_id: int
    cliente_id: int | None
    estado: SolicitudEstado
    created_at: datetime
    updated_at: datetime


class InvitationPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    asesor_id: int
    solicitud_id: int
    correo_objetivo: str | None
    tipo_identificacion: TipoIdentificacion | None
    numero_identificacion: str | None
    estado: InvitacionEstado
    created_at: datetime
    solicitud: SolicitudPublic
