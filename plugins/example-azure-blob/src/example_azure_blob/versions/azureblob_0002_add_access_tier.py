"""Add access_tier column

Revision ID: azureblob_0002_add_access_tier
Revises: azureblob_0001_create_table
Create Date: 2026-09-10

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "azureblob_0002_add_access_tier"
down_revision: Union[str, None] = "azureblob_0001_create_table"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "azure_blob_plugin_assets", sa.Column("access_tier", sa.String(), nullable=True)
    )


def downgrade() -> None:
    op.drop_column("azure_blob_plugin_assets", "access_tier")
