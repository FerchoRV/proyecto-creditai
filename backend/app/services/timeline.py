from __future__ import annotations

from fastapi import HTTPException, status

from app.models.solicitud import SolicitudEstado

ALLOWED_TRANSITIONS: dict[SolicitudEstado, set[SolicitudEstado]] = {
    SolicitudEstado.recibido: {SolicitudEstado.en_estudio, SolicitudEstado.rechazado},
    SolicitudEstado.en_estudio: {SolicitudEstado.aprobado, SolicitudEstado.rechazado},
    SolicitudEstado.aprobado: set(),
    SolicitudEstado.rechazado: set(),
}


def assert_transition_allowed(current: SolicitudEstado, nuevo: SolicitudEstado) -> None:
    allowed = ALLOWED_TRANSITIONS.get(current, set())
    if nuevo not in allowed:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Transición no permitida: {current.value} → {nuevo.value}",
        )


def next_states(current: SolicitudEstado) -> list[SolicitudEstado]:
    return sorted(ALLOWED_TRANSITIONS.get(current, set()), key=lambda s: s.value)
