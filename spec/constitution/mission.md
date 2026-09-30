# Misión

## Qué construimos

**CreditAI** es una plataforma web para asesores de crédito independientes y sus clientes. Permite registrar usuarios, vincular asesores con clientes mediante invitaciones a procesos de estudio, y dar seguimiento a cada solicitud con una línea de tiempo de estados.

Piezas principales:

1. **Autenticación y perfiles** — registro e inicio de sesión de asesores y clientes.
2. **Procesos de estudio** — solicitudes creadas por el asesor al invitar a un cliente; cada una tiene su propio ciclo de vida.
3. **Línea de tiempo** — historial visible del estado de cada solicitud (el cliente ve la suya; el asesor gestiona).

## Para quién

- **Asesor de crédito (independiente)** — registra clientes potenciales vía invitación, gestiona varios estudios y actualiza el estado de cada proceso.
- **Cliente / solicitante** — se registra, acepta o queda vinculado a procesos de estudio y consulta la línea de tiempo de su solicitud.
- **Equipo / autor del diplomado** — entregable con backend, frontend y base de datos containerizados.

## Principios

- **Dos roles claros** — asesor y cliente; permisos distintos (solo el asesor cambia estados).
- **El proceso es la unidad** — un mismo cliente puede tener varios estudios y varios asesores; el vínculo real vive en la solicitud/estudio.
- **Spec primero** — no se implementa sin `spec.md` → `plan.md` → `tasks.md` alineados a esta constitución.
- **Simple y desplegable** — tres contenedores (frontend, backend, Postgres); sin sobre-ingeniería en el MVP.
- **ML después** — la estimación de mora queda fuera del alcance actual; no contaminar el dominio ni el stack con eso aún.

## Qué NO es

- No es un core bancario ni un motor de scoring/ML (eso es backlog futuro).
- No es una red social ni un marketplace abierto de asesores.
- No incluye pagos, desembolsos ni firma electrónica de contratos.
- No es multi-tenant empresarial con jerarquías de supervisores (asesores son independientes).
