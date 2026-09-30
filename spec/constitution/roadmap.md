# Roadmap

## Hecho ✅

1. **001-autenticacion** — registro e inicio de sesión JWT para asesor y cliente.
2. **002-crud-usuarios** — consulta, edición y baja/desactivación de perfiles asesor y cliente.

## Siguiente 🔜

3. **003-invitacion** — el asesor invita al cliente y crea la solicitud/proceso (vínculo N:N vía estudios).

## Backlog ordenado 💡

4. **004-linea-tiempo** — historial de estados de la solicitud; solo el asesor cambia el estado.

### Más adelante (fuera del MVP actual)

- Estimación de mora / scoring con ML.
- Notificaciones por correo al cambiar estado.
- Panel de métricas para el asesor.
- Listado de clientes vinculados del asesor (depende de 003).

> Cada feature vive en `features/NNN-nombre-feature/` con `spec.md`, `plan.md` y `tasks.md` antes de tocar código.
