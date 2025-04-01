"""Add general settings

Revision ID: 269e6dbd565c
Revises: 2a58b7ce3cea
Create Date: 2025-02-28 15:05:41.442418

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy import orm

from app.theme_settings.model import SETTINGS_ID, ThemeSettings

# revision identifiers, used by Alembic.
revision: str = "269e6dbd565c"
down_revision: Union[str, None] = "2a58b7ce3cea"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "theme_settings",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("portal_name", sa.String),
    )

    # Adding initial data
    bind = op.get_bind()
    session = orm.Session(bind=bind)

    settings = ThemeSettings(id=SETTINGS_ID, portal_name="Data Product Portal")
    session.add(settings)
    session.commit()


def downgrade() -> None:
    op.drop_table("theme_settings")
