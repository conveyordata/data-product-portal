"""unique_external_id_and_name

Revision ID: 85073aa08de4
Revises: ab4a604ab521
Create Date: 2024-09-09 11:42:15.814941

"""

from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "85073aa08de4"
down_revision: Union[str, None] = "926e7e37f11e"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_unique_constraint(
        "uq_data_product",
        "data_products",
        ["external_id", "name"],
        postgresql_nulls_not_distinct=True,
    )
    op.create_unique_constraint(
        "uq_dataset",
        "datasets",
        ["external_id", "name"],
        postgresql_nulls_not_distinct=True,
    )


def downgrade() -> None:
    op.drop_constraint("uq_data_product", "data_products", type_="unique")
    op.drop_constraint("uq_dataset", "datasets", type_="unique")
