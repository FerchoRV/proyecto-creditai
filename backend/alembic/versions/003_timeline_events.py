"""create timeline_events

Revision ID: 003_timeline
Revises: 002_invitaciones
Create Date: 2026-09-30
"""

from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "003_timeline"
down_revision: Union[str, None] = "002_invitaciones"
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


def upgrade() -> None:
    op.create_table(
        "timeline_events",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column(
            "solicitud_id",
            sa.Integer(),
            sa.ForeignKey("solicitudes.id"),
            nullable=False,
        ),
        sa.Column("from_state", solicitud_estado, nullable=True),
        sa.Column("to_state", solicitud_estado, nullable=False),
        sa.Column("actor_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("nota", sa.String(length=280), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
    )
    op.create_index("ix_timeline_events_solicitud_id", "timeline_events", ["solicitud_id"])


def downgrade() -> None:
    op.drop_index("ix_timeline_events_solicitud_id", table_name="timeline_events")
    op.drop_table("timeline_events")
