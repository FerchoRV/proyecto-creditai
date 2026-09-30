from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.core.deps import get_current_user
from app.database import get_db
from app.models import Solicitud, TimelineEvent, User
from app.models.user import UserRole
from app.schemas.invitations import SolicitudPublic
from app.schemas.timeline import SolicitudDetail, TimelineEventPublic, TransitionRequest
from app.services.timeline import assert_transition_allowed, next_states

router = APIRouter(prefix="/api/v1/solicitudes", tags=["solicitudes"])


def _get_solicitud_or_404(db: Session, solicitud_id: int) -> Solicitud:
    solicitud = db.get(Solicitud, solicitud_id)
    if solicitud is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Solicitud no encontrada")
    return solicitud


def _ensure_can_view(user: User, solicitud: Solicitud) -> None:
    if user.rol == UserRole.asesor and solicitud.asesor_id == user.id:
        return
    if user.rol == UserRole.cliente and solicitud.cliente_id == user.id:
        return
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="No tienes acceso a esta solicitud",
    )


def _ensure_asesor_owner(user: User, solicitud: Solicitud) -> None:
    if user.rol != UserRole.asesor or solicitud.asesor_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo el asesor de la solicitud puede cambiar el estado",
        )


def _detail(solicitud: Solicitud, viewer: User) -> SolicitudDetail:
    events = sorted(solicitud.timeline_events, key=lambda e: e.created_at)
    available = next_states(solicitud.estado) if viewer.rol == UserRole.asesor and viewer.id == solicitud.asesor_id else []
    return SolicitudDetail(
        **SolicitudPublic.model_validate(solicitud).model_dump(),
        timeline=[TimelineEventPublic.model_validate(e) for e in events],
        transiciones_disponibles=available,
    )


@router.get("", response_model=list[SolicitudPublic])
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


@router.get("/{solicitud_id}", response_model=SolicitudDetail)
def get_solicitud(
    solicitud_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> SolicitudDetail:
    solicitud = db.scalar(
        select(Solicitud)
        .options(joinedload(Solicitud.timeline_events))
        .where(Solicitud.id == solicitud_id)
    )
    if solicitud is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Solicitud no encontrada")
    _ensure_can_view(current_user, solicitud)
    return _detail(solicitud, current_user)


@router.get("/{solicitud_id}/timeline", response_model=list[TimelineEventPublic])
def get_timeline(
    solicitud_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[TimelineEventPublic]:
    solicitud = _get_solicitud_or_404(db, solicitud_id)
    _ensure_can_view(current_user, solicitud)
    events = db.scalars(
        select(TimelineEvent)
        .where(TimelineEvent.solicitud_id == solicitud_id)
        .order_by(TimelineEvent.created_at.asc())
    ).all()
    return [TimelineEventPublic.model_validate(e) for e in events]


@router.post("/{solicitud_id}/transiciones", response_model=SolicitudDetail)
def transition_solicitud(
    solicitud_id: int,
    payload: TransitionRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> SolicitudDetail:
    solicitud = db.scalar(
        select(Solicitud)
        .options(joinedload(Solicitud.timeline_events))
        .where(Solicitud.id == solicitud_id)
    )
    if solicitud is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Solicitud no encontrada")

    _ensure_asesor_owner(current_user, solicitud)
    assert_transition_allowed(solicitud.estado, payload.nuevo_estado)

    evento = TimelineEvent(
        solicitud_id=solicitud.id,
        from_state=solicitud.estado,
        to_state=payload.nuevo_estado,
        actor_id=current_user.id,
        nota=payload.nota.strip() if payload.nota else None,
    )
    solicitud.estado = payload.nuevo_estado
    db.add(evento)
    db.commit()

    solicitud = db.scalar(
        select(Solicitud)
        .options(joinedload(Solicitud.timeline_events))
        .where(Solicitud.id == solicitud_id)
    )
    assert solicitud is not None
    return _detail(solicitud, current_user)
