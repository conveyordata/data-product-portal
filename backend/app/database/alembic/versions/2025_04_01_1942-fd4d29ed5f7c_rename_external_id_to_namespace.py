"""Rename external_id to namespace

Revision ID: fd4d29ed5f7c
Revises: c9b48c675202
Create Date: 2025-04-01 19:42:03.285296

"""

from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "fd4d29ed5f7c"
down_revision: Union[str, None] = "c9b48c675202"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column("data_products", "external_id", new_column_name="namespace")
    op.alter_column("datasets", "external_id", new_column_name="namespace")
    op.alter_column("data_outputs", "external_id", new_column_name="namespace")
    op.alter_column("data_product_settings", "external_id", new_column_name="namespace")


def downgrade() -> None:
    op.alter_column("data_products", "namespace", new_column_name="external_id")
    op.alter_column("datasets", "namespace", new_column_name="external_id")
    op.alter_column("data_outputs", "namespace", new_column_name="external_id")
    op.alter_column("data_product_settings", "namespace", new_column_name="external_id")
