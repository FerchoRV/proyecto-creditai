"""create users table

Revision ID: 001_users
Revises:
Create Date: 2026-09-30
"""

from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "001_users"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

tipo_identificacion = postgresql.ENUM(
    "CC", "CE", "PA", "NIT", name="tipo_identificacion", create_type=False
)
user_role = postgresql.ENUM("asesor", "cliente", name="user_role", create_type=False)
tipo_prestamo = postgresql.ENUM(
    "hipotecario",
    "libranza",
    "libre_inversion",
    name="tipo_prestamo",
    create_type=False,
)


def upgrade() -> None:
    bind = op.get_bind()
    postgresql.ENUM("CC", "CE", "PA", "NIT", name="tipo_identificacion").create(
        bind, checkfirst=True
    )
    postgresql.ENUM("asesor", "cliente", name="user_role").create(bind, checkfirst=True)
    postgresql.ENUM(
        "hipotecario", "libranza", "libre_inversion", name="tipo_prestamo"
    ).create(bind, checkfirst=True)

    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("nombre", sa.String(length=120), nullable=False),
        sa.Column("tipo_identificacion", tipo_identificacion, nullable=False),
        sa.Column("numero_identificacion", sa.String(length=40), nullable=False),
        sa.Column("correo", sa.String(length=255), nullable=False),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
        sa.Column("rol", user_role, nullable=False),
        sa.Column("salario", sa.Numeric(precision=14, scale=2), nullable=True),
        sa.Column("tipo_prestamo", tipo_prestamo, nullable=True),
        sa.Column("monto_prestamo", sa.Numeric(precision=14, scale=2), nullable=True),
        sa.Column("activo", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.UniqueConstraint(
            "tipo_identificacion",
            "numero_identificacion",
            name="uq_users_identificacion",
        ),
    )
    op.create_index("ix_users_correo", "users", ["correo"], unique=True)


def downgrade() -> None:
    op.drop_index("ix_users_correo", table_name="users")
    op.drop_table("users")
    bind = op.get_bind()
    postgresql.ENUM(name="tipo_prestamo").drop(bind, checkfirst=True)
    postgresql.ENUM(name="user_role").drop(bind, checkfirst=True)
    postgresql.ENUM(name="tipo_identificacion").drop(bind, checkfirst=True)
