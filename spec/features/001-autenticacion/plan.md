# 001 · Autenticación — Plan

## Enfoque

Implementar registro y login en FastAPI con hash de contraseña y JWT. El frontend Next.js consume esos endpoints y guarda el token para llamadas autenticadas. Los roles `asesor` y `cliente` se distinguen en el registro y quedan embebidos en el token o se resuelven desde el usuario.

## Implementación

1. Modelos de usuario (asesor/cliente o tabla `users` con `rol` + campos opcionales de cliente) y migración Alembic en `backend/`.
2. Endpoints: `POST /api/v1/auth/register`, `POST /api/v1/auth/login`, `GET /api/v1/auth/me`.
3. Utilidades de hash y emisión/verificación JWT; dependencia FastAPI `get_current_user`.
4. Pantallas Next.js de registro (elige rol) e inicio de sesión; cliente HTTP que envía `Authorization: Bearer …`.
5. Variables de entorno: `DATABASE_URL`, `JWT_SECRET`, etc., cableadas en Docker Compose.
6. Tests pytest de registro, login ok/fail y acceso a `/me` con/sin token.

## Decisiones

- **JWT en header Bearer** — simple para API + Next; se descarta sesión cookie-only en el MVP por simplicidad cross-origin entre contenedores.
- **Un solo recurso de auth con `rol`** — evita duplicar endpoints; campos de cliente se validan solo si `rol=cliente`.
- **Registro incluye datos de cliente** — aunque el CRUD (002) permita editarlos después, el alta inicial ya deja el perfil usable.

## Riesgos

- **Secret JWT débil en desarrollo** — documentar generación de secreto y no commitear `.env`.
- **Confusión rol en UI** — el formulario de registro debe dejar explícito asesor vs cliente.
- **Identificación duplicada** — constraint único en DB (tipo + número) además de validación en API.
