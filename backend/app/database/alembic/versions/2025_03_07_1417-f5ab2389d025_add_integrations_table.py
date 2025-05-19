"""add integrations table

Revision ID: f5ab2389d025
Revises: c643858b2670
Create Date: 2025-03-07 14:17:56.276522

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

from app.shared.model import utcnow


# revision identifiers, used by Alembic.
revision: str = 'f5ab2389d025'
down_revision: Union[str, None] = 'c643858b2670'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "integrations",
        sa.Column("uuid", sa.UUID, primary_key=True),
        sa.Column("integration_type", sa.String),
        sa.Column("url", sa.String),
        sa.Column("created_on", sa.DateTime(timezone=False), server_default=utcnow()),
        sa.Column("updated_on", sa.DateTime(timezone=False), onupdate=utcnow()),
    )

def downgrade() -> None:
    op.drop_table("integrations")
