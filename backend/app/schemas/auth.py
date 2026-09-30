from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, EmailStr, Field, model_validator

from app.models.user import TipoIdentificacion, TipoPrestamo, UserRole


class RegisterRequest(BaseModel):
    nombre: str = Field(min_length=2, max_length=120)
    tipo_identificacion: TipoIdentificacion
    numero_identificacion: str = Field(min_length=3, max_length=40)
    correo: EmailStr
    password: str = Field(min_length=8, max_length=128)
    rol: UserRole
    salario: Decimal | None = None
    tipo_prestamo: TipoPrestamo | None = None
    monto_prestamo: Decimal | None = None

    @model_validator(mode="after")
    def validate_cliente_fields(self) -> RegisterRequest:
        if self.rol == UserRole.cliente:
            missing = []
            if self.salario is None:
                missing.append("salario")
            if self.tipo_prestamo is None:
                missing.append("tipo_prestamo")
            if self.monto_prestamo is None:
                missing.append("monto_prestamo")
            if missing:
                raise ValueError(
                    "Para rol cliente son obligatorios: " + ", ".join(missing)
                )
            if self.salario is not None and self.salario < 0:
                raise ValueError("salario no puede ser negativo")
            if self.monto_prestamo is not None and self.monto_prestamo <= 0:
                raise ValueError("monto_prestamo debe ser mayor que 0")
        else:
            self.salario = None
            self.tipo_prestamo = None
            self.monto_prestamo = None
        return self


class LoginRequest(BaseModel):
    correo: EmailStr
    password: str = Field(min_length=1, max_length=128)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nombre: str
    tipo_identificacion: TipoIdentificacion
    numero_identificacion: str
    correo: EmailStr
    rol: UserRole
    salario: Decimal | None = None
    tipo_prestamo: TipoPrestamo | None = None
    monto_prestamo: Decimal | None = None
    activo: bool
    created_at: datetime


class AuthResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserPublic
