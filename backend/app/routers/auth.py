from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.core.security import create_access_token, hash_password, verify_password
from app.database import get_db
from app.models import User
from app.models.user import UserRole
from app.schemas.auth import (
    AuthResponse,
    LoginRequest,
    RegisterRequest,
    UserPublic,
)
from app.services.invitations import link_pending_invitations_for_cliente

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])


@router.post("/register", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
def register(payload: RegisterRequest, db: Session = Depends(get_db)) -> AuthResponse:
    correo = payload.correo.lower().strip()
    numero = payload.numero_identificacion.strip()

    existing_email = db.scalar(select(User).where(User.correo == correo))
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="El correo ya está registrado",
        )

    existing_id = db.scalar(
        select(User).where(
            User.tipo_identificacion == payload.tipo_identificacion,
            User.numero_identificacion == numero,
        )
    )
    if existing_id:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="La identificación ya está registrada",
        )

    user = User(
        nombre=payload.nombre.strip(),
        tipo_identificacion=payload.tipo_identificacion,
        numero_identificacion=numero,
        correo=correo,
        password_hash=hash_password(payload.password),
        rol=payload.rol,
        salario=payload.salario,
        tipo_prestamo=payload.tipo_prestamo,
        monto_prestamo=payload.monto_prestamo,
        activo=True,
    )
    db.add(user)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="No se pudo registrar: correo o identificación duplicados",
        ) from None
    db.refresh(user)

    if user.rol == UserRole.cliente:
        link_pending_invitations_for_cliente(db, user)
        db.refresh(user)

    token = create_access_token(user_id=user.id, rol=user.rol.value)
    return AuthResponse(access_token=token, user=UserPublic.model_validate(user))


@router.post("/login", response_model=AuthResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)) -> AuthResponse:
    correo = payload.correo.lower().strip()
    user = db.scalar(select(User).where(User.correo == correo))

    if user is None or not verify_password(payload.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Correo o contraseña incorrectos",
        )
    if not user.activo:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario desactivado",
        )

    token = create_access_token(user_id=user.id, rol=user.rol.value)
    return AuthResponse(access_token=token, user=UserPublic.model_validate(user))


@router.get("/me", response_model=UserPublic)
def me(current_user: User = Depends(get_current_user)) -> UserPublic:
    return UserPublic.model_validate(current_user)
