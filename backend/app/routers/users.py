from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.core.security import hash_password, verify_password
from app.database import get_db
from app.models import User
from app.models.user import UserRole
from app.schemas.auth import UserPublic
from app.schemas.users import PasswordChangeRequest, UserUpdateRequest

router = APIRouter(prefix="/api/v1/users", tags=["users"])


def _ensure_self(current_user: User, user_id: int) -> None:
    if current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No puedes acceder o modificar el perfil de otro usuario",
        )


def _apply_update(user: User, payload: UserUpdateRequest, db: Session) -> User:
    data = payload.model_dump(exclude_unset=True)

    if "correo" in data and data["correo"] is not None:
        nuevo_correo = str(data["correo"]).lower().strip()
        if nuevo_correo != user.correo:
            exists = db.scalar(
                select(User).where(User.correo == nuevo_correo, User.id != user.id)
            )
            if exists:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="El correo ya está registrado",
                )
            user.correo = nuevo_correo

    if "nombre" in data and data["nombre"] is not None:
        user.nombre = data["nombre"].strip()

    if user.rol == UserRole.cliente:
        if "salario" in data:
            user.salario = data["salario"]
        if "tipo_prestamo" in data:
            user.tipo_prestamo = data["tipo_prestamo"]
        if "monto_prestamo" in data:
            user.monto_prestamo = data["monto_prestamo"]
    else:
        # Asesor: ignore client-only fields if sent
        for key in ("salario", "tipo_prestamo", "monto_prestamo"):
            if key in data and data[key] is not None:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail=f"El campo {key} solo aplica a clientes",
                )

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="No se pudo actualizar: correo duplicado",
        ) from None
    db.refresh(user)
    return user


@router.get("/me", response_model=UserPublic)
def get_me(current_user: User = Depends(get_current_user)) -> UserPublic:
    return UserPublic.model_validate(current_user)


@router.patch("/me", response_model=UserPublic)
def update_me(
    payload: UserUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> UserPublic:
    user = db.get(User, current_user.id)
    assert user is not None
    updated = _apply_update(user, payload, db)
    return UserPublic.model_validate(updated)


@router.post("/me/password", response_model=UserPublic)
def change_password(
    payload: PasswordChangeRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> UserPublic:
    user = db.get(User, current_user.id)
    assert user is not None
    if not verify_password(payload.password_actual, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La contraseña actual es incorrecta",
        )
    user.password_hash = hash_password(payload.password_nueva)
    db.commit()
    db.refresh(user)
    return UserPublic.model_validate(user)


@router.delete("/me", status_code=status.HTTP_204_NO_CONTENT)
def deactivate_me(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Response:
    user = db.get(User, current_user.id)
    assert user is not None
    user.activo = False
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/{user_id}", response_model=UserPublic)
def get_user(
    user_id: int,
    current_user: User = Depends(get_current_user),
) -> UserPublic:
    _ensure_self(current_user, user_id)
    return UserPublic.model_validate(current_user)


@router.patch("/{user_id}", response_model=UserPublic)
def update_user(
    user_id: int,
    payload: UserUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> UserPublic:
    _ensure_self(current_user, user_id)
    user = db.get(User, current_user.id)
    assert user is not None
    updated = _apply_update(user, payload, db)
    return UserPublic.model_validate(updated)
