from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.core.deps import get_current_user, require_asesor
from app.database import get_db
from app.models import Invitacion, InvitacionEstado, Solicitud, SolicitudEstado, User
from app.models.user import UserRole
from app.schemas.invitations import (
    InvitationCreateRequest,
    InvitationPublic,
    SolicitudPublic,
)
from app.services.invitations import find_cliente_match

router = APIRouter(tags=["invitations"])


@router.post(
    "/api/v1/invitations",
    response_model=InvitationPublic,
    status_code=status.HTTP_201_CREATED,
)
def create_invitation(
    payload: InvitationCreateRequest,
    asesor: User = Depends(require_asesor),
    db: Session = Depends(get_db),
) -> InvitationPublic:
    correo = payload.correo.lower().strip() if payload.correo else None
    tipo = payload.tipo_identificacion
    numero = payload.numero_identificacion

    cliente = find_cliente_match(
        db,
        correo=correo,
        tipo_identificacion=tipo,
        numero_identificacion=numero,
    )

    if cliente is not None and cliente.id == asesor.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No puedes invitarte a ti mismo",
        )

    solicitud = Solicitud(
        asesor_id=asesor.id,
        cliente_id=cliente.id if cliente else None,
        estado=SolicitudEstado.recibido,
    )
    db.add(solicitud)
    db.flush()

    invitacion = Invitacion(
        asesor_id=asesor.id,
        solicitud_id=solicitud.id,
        correo_objetivo=correo,
        tipo_identificacion=tipo,
        numero_identificacion=numero,
        estado=(
            InvitacionEstado.vinculada if cliente else InvitacionEstado.pendiente
        ),
    )
    db.add(invitacion)
    db.commit()
    db.refresh(invitacion)
    invitacion = db.scalar(
        select(Invitacion)
        .options(joinedload(Invitacion.solicitud))
        .where(Invitacion.id == invitacion.id)
    )
    assert invitacion is not None
    return InvitationPublic.model_validate(invitacion)


@router.get("/api/v1/invitations", response_model=list[InvitationPublic])
def list_invitations(
    asesor: User = Depends(require_asesor),
    db: Session = Depends(get_db),
) -> list[InvitationPublic]:
    rows = db.scalars(
        select(Invitacion)
        .options(joinedload(Invitacion.solicitud))
        .where(Invitacion.asesor_id == asesor.id)
        .order_by(Invitacion.created_at.desc())
    ).unique().all()
    return [InvitationPublic.model_validate(row) for row in rows]


@router.get("/api/v1/solicitudes", response_model=list[SolicitudPublic])
def list_solicitudes(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[SolicitudPublic]:
    if current_user.rol == UserRole.asesor:
        rows = db.scalars(
            select(Solicitud)
            .where(Solicitud.asesor_id == current_user.id)
            .order_by(Solicitud.created_at.desc())
        ).all()
    elif current_user.rol == UserRole.cliente:
        rows = db.scalars(
            select(Solicitud)
            .where(Solicitud.cliente_id == current_user.id)
            .order_by(Solicitud.created_at.desc())
        ).all()
    else:
        rows = []
    return [SolicitudPublic.model_validate(row) for row in rows]
