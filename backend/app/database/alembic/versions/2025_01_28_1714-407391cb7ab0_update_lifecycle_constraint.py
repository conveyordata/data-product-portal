"""update lifecycle constraint

Revision ID: 407391cb7ab0
Revises: 2b231c9fb53a
Create Date: 2025-01-28 17:14:01.538692

"""

from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "407391cb7ab0"
down_revision: Union[str, None] = "2b231c9fb53a"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_constraint(
        "data_products_lifecycle_id_fkey", "data_products", type_="foreignkey"
    )
    op.create_foreign_key(
        "data_products_lifecycle_id_fkey",
        "data_products",
        "data_product_lifecycles",
        ["lifecycle_id"],
        ["id"],
        ondelete="SET NULL",
    )

    # Update the lifecycle_id foreign key on dataset to include ON DELETE SET NULL
    op.drop_constraint("datasets_lifecycle_id_fkey", "datasets", type_="foreignkey")
    op.create_foreign_key(
        "datasets_lifecycle_id_fkey",
        "datasets",
        "data_product_lifecycles",
        ["lifecycle_id"],
        ["id"],
        ondelete="SET NULL",
    )


def downgrade() -> None:
    op.drop_constraint(
        "data_products_lifecycle_id_fkey", "data_products", type_="foreignkey"
    )
    op.create_foreign_key(
        "data_products_lifecycle_id_fkey",
        "data_products",
        "data_product_lifecycles",
        ["lifecycle_id"],
        ["id"],
    )

    # Revert the lifecycle_id foreign key on dataset to remove ON DELETE SET NULL
    op.drop_constraint("datasets_lifecycle_id_fkey", "datasets", type_="foreignkey")
    op.create_foreign_key(
        "datasets_lifecycle_id_fkey",
        "datasets",
        "data_product_lifecycles",
        ["lifecycle_id"],
        ["id"],
    )
