"""Fix data product name namespace uniqueness constraint

Revision ID: c8a49838fa13
Revises: 3a883d3ec0f6
Create Date: 2026-04-17 16:23:53.138392

"""

from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "c8a49838fa13"
down_revision: Union[str, None] = "3a883d3ec0f6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("ALTER TABLE data_products DROP CONSTRAINT IF EXISTS uq_data_product")
    op.create_unique_constraint(
        "uq_data_product_name",
        "data_products",
        ["name"],
        postgresql_nulls_not_distinct=True,
    )
    op.create_unique_constraint(
        "uq_data_product_namespace",
        "data_products",
        ["namespace"],
        postgresql_nulls_not_distinct=True,
    )


def downgrade() -> None:
    op.execute(
        "ALTER TABLE data_products DROP CONSTRAINT IF EXISTS uq_data_product_name"
    )
    op.execute(
        "ALTER TABLE data_products DROP CONSTRAINT IF EXISTS uq_data_product_namespace"
    )
    op.create_unique_constraint(
        "uq_data_product",
        "data_products",
        ["namespace", "name"],
        postgresql_nulls_not_distinct=True,
    )
