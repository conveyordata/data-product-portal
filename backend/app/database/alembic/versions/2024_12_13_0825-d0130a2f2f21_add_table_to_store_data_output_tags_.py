"""Add table to store data output tags association

Revision ID: d0130a2f2f21
Revises: 3d6be1e9b5fa
Create Date: 2024-12-13 08:25:04.909541

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import UUID

from app.shared.model import utcnow

# revision identifiers, used by Alembic.
revision: str = "d0130a2f2f21"
down_revision: Union[str, None] = "3d6be1e9b5fa"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "tags_data_outputs",
        sa.Column("data_output_id", UUID, sa.ForeignKey("data_outputs.id")),
        sa.Column("tag_id", UUID, sa.ForeignKey("tags.id")),
        sa.Column("created_on", sa.DateTime(timezone=False), server_default=utcnow()),
        sa.Column("updated_on", sa.DateTime(timezone=False), onupdate=utcnow()),
    )


def downgrade() -> None:
    op.drop_table("tags_data_outputs")
