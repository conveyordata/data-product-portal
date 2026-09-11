"""Add plugin_migration_state table

Revision ID: a7c2e8f1d3b4
Revises: f3a1c9d4b6e2
Create Date: 2026-09-11 09:05:00.000000

The portal pre-creates this as a normal Alembic version table (a single
`version_num` primary key column - the exact shape Alembic itself would
create automatically), except with a wider column than Alembic's own
32-character default. Alembic only auto-creates a version table when one
doesn't already exist yet, so pre-creating it here with room for
descriptive, plugin-key-prefixed revision ids (see
app/plugins/migrations.py) avoids a `StringDataRightTruncation` error the
first time a plugin with a longer revision id is reconciled - found by
actually exercising this against a real revision id during the spike.
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "a7c2e8f1d3b4"
down_revision: Union[str, None] = "f3a1c9d4b6e2"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "plugin_migration_state",
        sa.Column("version_num", sa.String(255), nullable=False),
        sa.PrimaryKeyConstraint("version_num", name="plugin_migration_state_pkc"),
    )


def downgrade() -> None:
    op.drop_table("plugin_migration_state")
