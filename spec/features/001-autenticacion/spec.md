# 001 · Autenticación

**Estado:** propuesta

## Qué hace

Permite a asesores y clientes **registrarse** e **iniciar sesión** en CreditAI. Tras autenticarse, la sesión (token) identifica al usuario y su rol para el resto de la app.

## Por qué

Sin autenticación no hay identidad ni permisos. Es la base del resto de features (CRUD, invitación, línea de tiempo) y un requisito explícito desde el inicio.

## Criterios de aceptación

- [ ] Un usuario puede registrarse como **asesor** con: nombre, tipo de identificación, número de identificación, correo y contraseña.
- [ ] Un usuario puede registrarse como **cliente** con los campos del asesor más: salario, tipo de préstamo (`hipotecario` | `libranza` | `libre_inversion`) y monto del préstamo.
- [ ] El correo es único; la combinación tipo+número de identificación es única.
- [ ] La contraseña se almacena hasheada (nunca en texto plano).
- [ ] Un usuario registrado puede iniciar sesión con correo y contraseña y recibe un token JWT válido.
- [ ] Credenciales inválidas o usuario inexistente responden con error claro (sin filtrar datos sensibles).
- [ ] Un endpoint (o equivalente) permite obtener el perfil del usuario autenticado a partir del token.
- [ ] Rutas protegidas del API rechazan peticiones sin token válido.

## Fuera de alcance

- Recuperación / reset de contraseña por correo.
- OAuth / login social.
- Refresh tokens rotativos avanzados (se puede usar un JWT simple de access en el MVP).
- CRUD completo de perfil (eso es la feature 002).
- Invitaciones y solicitudes (features 003–004).
