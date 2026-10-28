"""Add output port announcements

Revision ID: c41e7a9d2b58
Revises: a9203b7e41cd
Create Date: 2026-10-28 12:00:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

from app.shared.model import utcnow

# revision identifiers, used by Alembic.
revision: str = "c41e7a9d2b58"
down_revision: Union[str, None] = "a9203b7e41cd"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "output_port_announcements",
        sa.Column("id", sa.UUID, primary_key=True),
        sa.Column(
            "output_port_id",
            sa.UUID,
            sa.ForeignKey("datasets.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("type", sa.String(), nullable=False),
        sa.Column("title", sa.String(length=100), nullable=False),
        sa.Column("message", sa.Text(), nullable=False),
        sa.Column("link", sa.Text(), nullable=True),
        sa.Column(
            "author_id",
            sa.UUID,
            sa.ForeignKey("users.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=utcnow(),
        ),
    )
    op.create_index(
        "ix_output_port_announcements_output_port_id",
        "output_port_announcements",
        ["output_port_id"],
    )

    entities = sa.table("event_reference_entities", sa.column("key", sa.String))
    op.bulk_insert(entities, [{"key": "ANNOUNCEMENT"}])


def downgrade() -> None:

    events = sa.table("events", sa.column("target_type", sa.String))
    op.execute(events.delete().where(events.c.target_type == "ANNOUNCEMENT"))
    entities = sa.table("event_reference_entities", sa.column("key", sa.String))
    op.execute(entities.delete().where(entities.c.key == "ANNOUNCEMENT"))

    op.drop_index(
        "ix_output_port_announcements_output_port_id",
        table_name="output_port_announcements",
    )
    op.drop_table("output_port_announcements")
