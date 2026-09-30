# 004 · Línea de tiempo del proceso — Plan

## Enfoque

Tabla `timeline_events` (o `solicitud_eventos`) ligada a `solicitudes`. Un endpoint de transición de estado valida la máquina de estados, actualiza `solicitud.estado` y append-only del evento. Frontend: detalle de solicitud con timeline.

## Implementación

1. Migración: `timeline_events` (solicitud_id, from_state, to_state, actor_id, created_at, opcional nota corta).
2. Al crear solicitud (003): insertar evento inicial `→ recibido`.
3. Endpoint asesor: `POST /api/v1/solicitudes/{id}/transiciones` con `{ "nuevo_estado": "..." }`.
4. Endpoint lectura: `GET /api/v1/solicitudes/{id}` + `GET .../timeline` (o embebido).
5. Máquina de estados: `recibido → en_estudio → aprobado|rechazado`; opcional `recibido → rechazado`.
6. UI: vista detalle asesor (acciones de estado) y vista cliente (solo lectura).
7. Tests de transiciones válidas/inválidas y permisos cliente vs asesor.

## Decisiones

- **Append-only en eventos** — no se editan ni borran; auditoría simple.
- **Estados terminales** — `aprobado` y `rechazado` no revierten en el MVP.
- **Nota opcional corta** en la transición — útil sin abrir feature de comentarios.

## Riesgos

- **Dependencia fuerte de 003** — no implementar sin solicitudes.
- **Desalineación UI/API** — compartir enum de estados en contrato (OpenAPI / tipos TS).
