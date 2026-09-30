# 002 · CRUD de usuarios — Plan

## Enfoque

Exponer recursos REST de perfil sobre el modelo de usuario de la feature 001. El frontend ofrece pantalla de “Mi perfil” (y, cuando exista 003, listados de clientes del asesor). Preferir soft-delete (`activo=false`) frente a borrado físico.

## Implementación

1. Extender modelo con flag `activo` si no existe; migración.
2. Endpoints: `GET/PATCH /api/v1/users/me`, `DELETE /api/v1/users/me` (o `POST .../deactivate`).
3. Validaciones Pydantic separadas para update de asesor vs cliente.
4. UI Next.js: página de perfil con formulario según rol.
5. Tests de update propio, intento de update ajeno, desactivación e impacto en login.

## Decisiones

- **Soft-delete** — conserva historial de solicitudes futuras; se descarta hard-delete en MVP.
- **Identificación inmutable tras el alta** — reduce fraude de identidad; cambios excepcionales fuera de alcance.
- **Listado de clientes del asesor** — se completa de verdad con 003; en 002 basta el CRUD de “me” si 003 no está listo (marcar dependencia).

## Riesgos

- **Dependencia con 003** — no bloquear el CRUD de perfil propio; listados N:N se integran al cerrar invitación.
- **Cambio de correo** — debe respetar unicidad y no romper invitaciones pendientes ligadas a email.
