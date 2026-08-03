"""Add general settings

Revision ID: 269e6dbd565c
Revises: d98efbda5e7c
Create Date: 2025-02-28 15:05:41.442418

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

from app.configuration.theme_settings.model import SETTINGS_ID

# revision identifiers, used by Alembic.
revision: str = "269e6dbd565c"
down_revision: Union[str, None] = "d98efbda5e7c"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "theme_settings",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("portal_name", sa.String),
    )

    op.bulk_insert(
        sa.table(
            "theme_settings",
            sa.column("id", sa.Integer),
            sa.column("portal_name", sa.String),
        ),
        [{"id": SETTINGS_ID, "portal_name": "Data Product Portal"}],
    )


def downgrade() -> None:
    op.drop_table("theme_settings")
