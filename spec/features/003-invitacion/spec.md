# 003 · Invitación a estudio

**Estado:** implementado ✅

## Qué hace

El **asesor invita** a un cliente a un proceso de estudio. Eso crea (o deja pendiente) el vínculo y una **solicitud** asociada. Un asesor puede tener muchos clientes y muchas solicitudes; un cliente puede tener varios asesores y varios estudios (relación muchos-a-muchos materializada por solicitudes/invitaciones).

## Por qué

Sin invitación no hay proceso compartido: el registro independiente no basta para relacionar asesor y cliente. Es el núcleo operativo de CreditAI antes de la línea de tiempo.

## Criterios de aceptación

- [x] Un asesor autenticado puede crear una **invitación** indicando al cliente por **correo** y/o **tipo+número de identificación**.
- [x] Al invitar, se crea una **solicitud** en estado inicial `recibido` vinculada al asesor.
- [x] Si el cliente **ya está registrado**, la solicitud queda vinculada de inmediato a ese cliente.
- [x] Si el cliente **aún no existe**, la invitación queda **pendiente** y se vincula automáticamente cuando el cliente se registre con el mismo correo o la misma identificación.
- [x] Un mismo par asesor–cliente puede tener **varias solicitudes** (estudios distintos) a lo largo del tiempo.
- [x] Un cliente puede tener solicitudes con **distintos asesores**.
- [x] El asesor puede **listar** sus invitaciones/solicitudes y ver el estado de vinculación (pendiente vs activa).
- [x] El cliente autenticado puede **listar** las solicitudes/estudios en los que participa.
- [x] Un cliente **no** puede crear invitaciones ni solicitudes.
- [x] No se crean vínculos duplicados espurios: cada invitación genera su propia solicitud; no se fusionan estudios distintos.

## Fuera de alcance

- Cambio de estados `en_estudio` / `aprobado` / `rechazado` y historial detallado (feature 004).
- Envío real de correo electrónico (puede mostrarse el token/enlace en UI o logs en MVP).
- Estimación de mora / ML.
- Chat o mensajería entre asesor y cliente.
