from __future__ import annotations

from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.models import Invitacion, InvitacionEstado, Solicitud, User
from app.models.user import TipoIdentificacion, UserRole


def find_cliente_match(
    db: Session,
    *,
    correo: str | None,
    tipo_identificacion: TipoIdentificacion | None,
    numero_identificacion: str | None,
) -> User | None:
    if correo:
        user = db.scalar(
            select(User).where(
                User.rol == UserRole.cliente,
                User.correo == correo.lower().strip(),
                User.activo.is_(True),
            )
        )
        if user:
            return user

    if tipo_identificacion and numero_identificacion:
        user = db.scalar(
            select(User).where(
                User.rol == UserRole.cliente,
                User.tipo_identificacion == tipo_identificacion,
                User.numero_identificacion == numero_identificacion.strip(),
                User.activo.is_(True),
            )
        )
        if user:
            return user
    return None


def link_pending_invitations_for_cliente(db: Session, cliente: User) -> int:
    """Vincula invitaciones pendientes que coincidan por correo o identificación."""
    if cliente.rol != UserRole.cliente:
        return 0

    conditions = [Invitacion.correo_objetivo == cliente.correo]
    conditions.append(
        (Invitacion.tipo_identificacion == cliente.tipo_identificacion)
        & (Invitacion.numero_identificacion == cliente.numero_identificacion)
    )

    pendientes = db.scalars(
        select(Invitacion).where(
            Invitacion.estado == InvitacionEstado.pendiente,
            or_(*conditions),
        )
    ).all()

    linked = 0
    for inv in pendientes:
        solicitud = db.get(Solicitud, inv.solicitud_id)
        if solicitud is None:
            continue
        if solicitud.cliente_id is not None and solicitud.cliente_id != cliente.id:
            continue
        solicitud.cliente_id = cliente.id
        inv.estado = InvitacionEstado.vinculada
        linked += 1

    if linked:
        db.commit()
    return linked
