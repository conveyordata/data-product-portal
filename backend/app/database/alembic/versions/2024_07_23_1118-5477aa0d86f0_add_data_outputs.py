"""add data outputs

Revision ID: 5477aa0d86f0
Revises: 4e61079eaf16
Create Date: 2024-07-23 11:18:30.435296

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

from app.data_outputs.data_output_types import DataOutputTypes
from app.shared.model import utcnow

# revision identifiers, used by Alembic.
revision: str = "5477aa0d86f0"
down_revision: Union[str, None] = "4e61079eaf16"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "data_outputs",
        sa.Column("id", sa.UUID, primary_key=True),
        sa.Column("name", sa.String),
        sa.Column("owner_id", sa.UUID, sa.ForeignKey("data_products.id")),
        # sa.Column("implementations", list[sa.UUID]),
        sa.Column("configuration", sa.String),
        sa.Column("configuration_type", sa.Enum(DataOutputTypes)),
        # sa.Column("account_id", sa.String),
        # sa.Column("kms_key", sa.String),
        sa.Column("created_on", sa.DateTime(timezone=False), server_default=utcnow()),
        sa.Column("updated_on", sa.DateTime(timezone=False), onupdate=utcnow()),
        sa.Column("deleted_at", sa.DateTime),
    )


def downgrade() -> None:
    pass
