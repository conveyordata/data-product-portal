"""add dataset custom settings

Revision ID: c5730551b99e
Revises: 407391cb7ab0
Create Date: 2025-01-29 09:56:11.153682

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "c5730551b99e"
down_revision: Union[str, None] = "407391cb7ab0"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("data_product_settings", sa.Column("scope", sa.String))
    op.execute(
        "UPDATE data_product_settings SET scope = 'DATAPRODUCT' WHERE scope IS NULL"
    )

    op.add_column(
        "data_products_settings_values",
        sa.Column(
            "dataset_id",
            sa.UUID(as_uuid=True),
            sa.ForeignKey("datasets.id", ondelete="CASCADE"),
        ),
    )


def downgrade() -> None:
    op.drop_column("data_product_settings", "scope")
    op.drop_column("data_products_settings_values", "dataset_id")
