# 003 · Invitación a estudio — Plan

## Enfoque

Modelar `Invitation` y/o `Application` (solicitud) en Postgres. El asesor crea el registro; un job lógico en el registro de cliente (hook post-register) resuelve invitaciones pendientes por correo o identificación. La N:N asesor↔cliente emerge de las solicitudes.

## Implementación

1. Migraciones: tablas `solicitudes` (asesor_id, cliente_id nullable, estado, timestamps) e `invitaciones` (asesor_id, email y/o identificación objetivo, solicitud_id, estado pendiente/aceptada).
2. Endpoints asesor: `POST /api/v1/invitations`, `GET /api/v1/invitations` (o `/solicitudes`).
3. Endpoints cliente: `GET /api/v1/solicitudes` (solo las suyas).
4. En `register` de cliente: buscar invitaciones pendientes coincidentes y enlazar `cliente_id`.
5. UI asesor: formulario “Invitar cliente” + listado de procesos.
6. UI cliente: listado de estudios/procesos vinculados.
7. Tests: invitar cliente existente, invitar inexistente + registro posterior, multi-asesor, multi-solicitud mismo cliente.

## Decisiones

- **Solicitud como entidad central** — la N:N no es una tabla puente vacía; cada estudio es una fila con estado.
- **cliente_id nullable hasta vincular** — permite invitar antes del registro.
- **Matching por correo o identificación** — maximiza chance de vincular; documentar prioridad si ambos vienen (p. ej. match si cualquiera coincide de forma única).

## Riesgos

- **Colisión de matching** — dos invitaciones ambiguas; exigir unicidad de email e identificación ayuda.
- **Spam de invitaciones** — rate limit simple o límite por asesor en MVP documentado.
- **Orden con 001/002** — requiere auth y usuarios; implementar después de 001 (002 puede ir en paralelo parcial).
