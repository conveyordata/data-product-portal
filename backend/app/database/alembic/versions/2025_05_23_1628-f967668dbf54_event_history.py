"""event history

Revision ID: f967668dbf54
Revises: 6441623a586b
Create Date: 2025-05-23 16:28:28.024986

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

from app.shared.model import utcnow

# revision identifiers, used by Alembic.
revision: str = "f967668dbf54"
down_revision: Union[str, None] = "6441623a586b"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "event_reference_entities",
        sa.Column("key", sa.String, primary_key=True, nullable=False),
    )
    op.bulk_insert(
        sa.table("event_reference_entities", sa.column("key", sa.String)),
        [{"key": k} for k in ("DATA_PRODUCT", "DATASET", "DATA_OUTPUT", "USER")],
    )

    op.create_table(
        "events",
        sa.Column("id", sa.UUID, primary_key=True, nullable=False),
        sa.Column("name", sa.String, nullable=False),
        sa.Column("subject_id", sa.UUID),
        sa.Column("target_id", sa.UUID, nullable=True),
        sa.Column(
            "subject_type",
            sa.String,
            sa.ForeignKey("event_reference_entities.key"),
            nullable=False,
        ),
        sa.Column(
            "target_type",
            sa.String,
            sa.ForeignKey("event_reference_entities.key"),
            nullable=True,
        ),
        sa.Column("deleted_subject_identifier", sa.String, nullable=True),
        sa.Column("deleted_target_identifier", sa.String, nullable=True),
        sa.Column("actor_id", sa.UUID, sa.ForeignKey("users.id"), nullable=False),
        sa.Column("created_on", sa.DateTime(timezone=False), server_default=utcnow()),
        sa.Column("updated_on", sa.DateTime(timezone=False), onupdate=utcnow()),
        sa.Column("deleted_at", sa.DateTime),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("index_events_subject", "events", ["subject_type", "subject_id"])
    op.create_index("index_events_target", "events", ["target_type", "target_id"])


def downgrade() -> None:
    op.drop_index("index_events_subject", table_name="events")
    op.drop_index("index_events_target", table_name="events")
    op.drop_table("events")
    op.drop_table("event_reference_entities")
