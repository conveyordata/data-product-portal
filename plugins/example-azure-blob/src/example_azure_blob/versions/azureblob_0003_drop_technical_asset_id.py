"""Drop technical_asset_id - id is now the technical asset's own id

Revision ID: azureblob_0003_drop_technical_asset_id
Revises: azureblob_0002_add_access_tier
Create Date: 2026-09-11

"""

from typing import Sequence, Union

from alembic import op

revision: str = "azureblob_0003_drop_technical_asset_id"
down_revision: Union[str, None] = "azureblob_0002_add_access_tier"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_column("azure_blob_plugin_assets", "technical_asset_id")


def downgrade() -> None:
    import sqlalchemy as sa
    from sqlalchemy.dialects import postgresql

    op.add_column(
        "azure_blob_plugin_assets",
        sa.Column("technical_asset_id", postgresql.UUID(as_uuid=True), nullable=True),
    )
