from __future__ import annotations

from decimal import Decimal

from pydantic import BaseModel, EmailStr, Field, model_validator

from app.models.user import TipoPrestamo
from app.schemas.auth import UserPublic

__all__ = ["UserPublic", "UserUpdateRequest", "PasswordChangeRequest"]


class UserUpdateRequest(BaseModel):
    nombre: str | None = Field(default=None, min_length=2, max_length=120)
    correo: EmailStr | None = None
    salario: Decimal | None = None
    tipo_prestamo: TipoPrestamo | None = None
    monto_prestamo: Decimal | None = None

    @model_validator(mode="after")
    def validate_amounts(self) -> UserUpdateRequest:
        if self.salario is not None and self.salario < 0:
            raise ValueError("salario no puede ser negativo")
        if self.monto_prestamo is not None and self.monto_prestamo <= 0:
            raise ValueError("monto_prestamo debe ser mayor que 0")
        return self


class PasswordChangeRequest(BaseModel):
    password_actual: str = Field(min_length=1, max_length=128)
    password_nueva: str = Field(min_length=8, max_length=128)
