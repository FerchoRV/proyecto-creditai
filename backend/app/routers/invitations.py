from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.core.deps import require_asesor
from app.database import get_db
from app.models import Invitacion, InvitacionEstado, Solicitud, SolicitudEstado, TimelineEvent, User
from app.schemas.invitations import (
    InvitationCreateRequest,
    InvitationPublic,
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

    db.add(
        TimelineEvent(
            solicitud_id=solicitud.id,
            from_state=None,
            to_state=SolicitudEstado.recibido,
            actor_id=asesor.id,
            nota="Solicitud creada",
        )
    )

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
