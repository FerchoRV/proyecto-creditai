# 004 · Línea de tiempo del proceso

**Estado:** implementado ✅

## Qué hace

Cada solicitud tiene una **línea de tiempo** de su gestión. El **asesor** avanza o cierra el estado (`recibido` → `en_estudio` → `aprobado` | `rechazado`). El **cliente** solo **consulta** el historial y el estado actual de sus procesos.

## Por qué

Da transparencia al solicitante y control al asesor. Es el valor visible del proceso de estudio una vez existe la invitación (003).

## Criterios de aceptación

- [x] Toda solicitud nueva empieza en `recibido` y tiene al menos un evento inicial en la línea de tiempo.
- [x] El asesor propietario de la solicitud puede cambiar el estado a `en_estudio`, `aprobado` o `rechazado` según transiciones permitidas.
- [x] Cada cambio de estado genera un **evento** con: estado anterior, estado nuevo, fecha/hora y asesor que lo realizó.
- [x] Transiciones inválidas se rechazan (p. ej. de `aprobado` a `en_estudio` si se define como terminal).
- [x] El cliente puede ver el estado actual y la línea de tiempo **solo** de sus solicitudes.
- [x] El asesor puede ver y mutar **solo** las solicitudes donde es el asesor vinculado.
- [x] El cliente **no** puede cambiar estados (403).
- [x] La UI muestra la línea de tiempo de forma cronológica legible.

## Fuera de alcance

- Comentarios libres / adjuntos por evento (se puede añadir después).
- Notificaciones por email/push al cambiar estado.
- Reapertura de solicitudes terminales (salvo que se decida explícitamente una transición; por defecto `aprobado` y `rechazado` son finales).
- ML / estimación de mora.
