# 002 · CRUD de usuarios

**Estado:** propuesta

## Qué hace

Permite **consultar, actualizar y desactivar/eliminar** perfiles de usuario (asesor y cliente) según permisos: cada usuario gestiona su propio perfil; operaciones de listado acotadas al rol (p. ej. un asesor no edita datos sensibles de otro asesor).

## Por qué

El registro (001) solo da de alta. Hace falta mantener los datos del perfil (nombre, contacto, salario, intención de préstamo del cliente, etc.) de forma explícita y segura.

## Criterios de aceptación

- [ ] Un usuario autenticado puede **ver su propio perfil** completo según su rol.
- [ ] Un usuario autenticado puede **actualizar** los campos editables de su perfil (nombre, correo con unicidad, datos de cliente si aplica). No puede cambiar su rol por sí mismo.
- [ ] La contraseña solo se cambia mediante un flujo dedicado (opcional en esta feature) o campo explícito; nunca se expone el hash.
- [ ] Identificación (tipo + número): editable solo si se mantiene la unicidad; o queda inmutable — documentado e implementado de forma consistente.
- [ ] Existe operación de **baja o desactivación** del propio usuario (soft-delete preferible) que impide nuevos logins.
- [ ] Un asesor autenticado puede **listar los clientes vinculados a él** (vía solicitudes/invitaciones cuando existan; si 003 aún no está, el listado global de clientes queda limitado o diferido — ver fuera de alcance).
- [ ] Endpoints responden 401 sin auth y 403 si se intenta mutar el perfil de otro usuario sin permiso.

## Fuera de alcance

- Administración global tipo “superadmin”.
- Invitación y creación de solicitudes (003).
- Línea de tiempo (004).
- Listado masivo de todos los usuarios del sistema para cualquier rol.
