# Tech stack y convenciones

## Tecnologías

- **Backend:** Python 3.12+ con FastAPI
- **Frontend:** Next.js (App Router) con TypeScript
- **Base de datos:** PostgreSQL
- **ORM / acceso a datos (backend):** SQLAlchemy + Alembic (migraciones)
- **Auth:** JWT (access token); contraseñas con hash (bcrypt o argon2)
- **Contenedores:** Docker Compose — 3 servicios: `frontend`, `backend`, `db`
- **Tests backend:** pytest
- **Tests frontend:** lo mínimo viable del stack Next (o validación manual documentada al inicio)
- **Despliegue:** local vía `docker compose up` (producción fuera de alcance del MVP)

## Archivos / módulos clave

- `spec/` — constitución y features (SDD); manda sobre el código.
- `backend/` — API FastAPI, modelos, migraciones, tests.
- `frontend/` — app Next.js (UI asesor y cliente).
- `docker-compose.yml` — orquestación de los tres contenedores (en la raíz del repo).

## Comandos

- `docker compose up --build` — arranca frontend, backend y Postgres.
- `docker compose exec backend pytest` — tests del backend.
- `docker compose exec backend alembic upgrade head` — migraciones.
- Comandos de lint/build concretos se fijan al crear el esqueleto del repo.

## Modelo de datos / dominio

- **Usuario** — base común: `nombre`, `tipo_identificacion` + `numero_identificacion`, `correo`, `password_hash`, `rol` (`asesor` | `cliente`).
- **Asesor** — perfil de rol asesor (sin campos de préstamo).
- **Cliente** — además: `salario`, y en registro MVP también `tipo_prestamo` (`hipotecario` | `libranza` | `libre_inversion`) y `monto_prestamo` (intención inicial; cada solicitud puede contextualizar el proceso).
- **Solicitud / estudio** — unidad de proceso: vincula un `asesor` y un `cliente`; `estado` ∈ {`recibido`, `en_estudio`, `aprobado`, `rechazado`}; un asesor puede tener varias solicitudes; un cliente puede tener varias (con el mismo u otros asesores). La relación muchos-a-muchos asesor↔cliente se materializa a través de solicitudes (e invitaciones).
- **Invitación** — el asesor inicia el vínculo/proceso; si el cliente aún no existe, queda pendiente hasta que se registre con el mismo correo/identificación.
- **Evento de línea de tiempo** — registro histórico de cambios de estado (quién, cuándo, de→a); solo el asesor muta el estado.
- **Identificación** — siempre `tipo` + `numero` (p. ej. CC, CE, pasaporte); únicos por combinación tipo+número.

## Convenciones

- Idioma de UI y mensajes de dominio: **español**.
- Código: inglés en identificadores (`snake_case` Python, `camelCase`/`PascalCase` en TS); comentarios solo si aportan.
- API REST bajo `/api/v1/...`; errores con cuerpo JSON consistente.
- Validación de entrada en backend (Pydantic) y formularios en frontend.
- Secretos solo en variables de entorno / `.env` (nunca en el repo).
- Spec antes que código: respetar `mission.md` y este archivo.

## Estilo visual

- Marca: **CreditAI**.
- UI limpia y funcional orientada a formularios y listados (asesor) y consulta de proceso (cliente).
- Tokens y tipografía se definen al implementar el frontend; evitar temas genéricos “AI purple”.

## Límites duros

- No añadir microservicios ni colas en el MVP: un solo backend FastAPI.
- No implementar modelos de ML ni estimación de mora en estas features.
- No subir `.env`, secretos ni dumps de base de datos al repositorio.
- No cambiar estados de solicitud desde el rol cliente.
- No contradecir la constitución: si una feature choca, se replantea la feature.
