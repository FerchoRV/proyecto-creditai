"""create solicitudes and invitaciones

Revision ID: 002_invitaciones
Revises: 001_users
Create Date: 2026-09-30
"""

from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "002_invitaciones"
down_revision: Union[str, None] = "001_users"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

solicitud_estado = postgresql.ENUM(
    "recibido",
    "en_estudio",
    "aprobado",
    "rechazado",
    name="solicitud_estado",
    create_type=False,
)
invitacion_estado = postgresql.ENUM(
    "pendiente",
    "vinculada",
    name="invitacion_estado",
    create_type=False,
)
tipo_identificacion = postgresql.ENUM(
    "CC",
    "CE",
    "PA",
    "NIT",
    name="tipo_identificacion",
    create_type=False,
)


def upgrade() -> None:
    bind = op.get_bind()
    postgresql.ENUM(
        "recibido", "en_estudio", "aprobado", "rechazado", name="solicitud_estado"
    ).create(bind, checkfirst=True)
    postgresql.ENUM("pendiente", "vinculada", name="invitacion_estado").create(
        bind, checkfirst=True
    )

    op.create_table(
        "solicitudes",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("asesor_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("cliente_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("estado", solicitud_estado, nullable=False, server_default="recibido"),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
    )
    op.create_index("ix_solicitudes_asesor_id", "solicitudes", ["asesor_id"])
    op.create_index("ix_solicitudes_cliente_id", "solicitudes", ["cliente_id"])

    op.create_table(
        "invitaciones",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("asesor_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column(
            "solicitud_id",
            sa.Integer(),
            sa.ForeignKey("solicitudes.id"),
            nullable=False,
            unique=True,
        ),
        sa.Column("correo_objetivo", sa.String(length=255), nullable=True),
        sa.Column("tipo_identificacion", tipo_identificacion, nullable=True),
        sa.Column("numero_identificacion", sa.String(length=40), nullable=True),
        sa.Column(
            "estado",
            invitacion_estado,
            nullable=False,
            server_default="pendiente",
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
    )
    op.create_index("ix_invitaciones_asesor_id", "invitaciones", ["asesor_id"])
    op.create_index("ix_invitaciones_correo_objetivo", "invitaciones", ["correo_objetivo"])


def downgrade() -> None:
    op.drop_index("ix_invitaciones_correo_objetivo", table_name="invitaciones")
    op.drop_index("ix_invitaciones_asesor_id", table_name="invitaciones")
    op.drop_table("invitaciones")
    op.drop_index("ix_solicitudes_cliente_id", table_name="solicitudes")
    op.drop_index("ix_solicitudes_asesor_id", table_name="solicitudes")
    op.drop_table("solicitudes")
    bind = op.get_bind()
    postgresql.ENUM(name="invitacion_estado").drop(bind, checkfirst=True)
    postgresql.ENUM(name="solicitud_estado").drop(bind, checkfirst=True)
