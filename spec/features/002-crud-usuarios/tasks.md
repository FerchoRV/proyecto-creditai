# 002 · CRUD de usuarios — Tareas

- [x] Campo `activo` ya existía desde 001 (sin migración nueva).
- [x] Implementar `GET` / `PATCH` de `/users/me` con validación por rol.
- [x] Implementar desactivación/baja de `/users/me` e impedir login si `activo=false`.
- [x] Fijar regla: identificación inmutable post-registro.
- [x] UI Next.js: página “Mi perfil” (asesor y cliente) con edición, password y baja.
- [x] Tests pytest de permisos y unicidad en updates.
- [x] Validar contra los criterios de aceptación de `spec.md`.
- [x] Mover la feature a "Hecho" en `../../constitution/roadmap.md`.
