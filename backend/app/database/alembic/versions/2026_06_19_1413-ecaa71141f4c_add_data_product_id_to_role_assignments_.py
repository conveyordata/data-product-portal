"""add_data_product_id_to_role_assignments_dataset

Revision ID: ecaa71141f4c
Revises: a07fd336c073
Create Date: 2026-06-19 14:13:52.188262

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "ecaa71141f4c"
down_revision: Union[str, None] = "a07fd336c073"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "role_assignments_dataset",
        sa.Column("data_product_id", sa.UUID(), nullable=True),
    )
    op.execute(
        """
        UPDATE role_assignments_dataset rad
        SET data_product_id = d.data_product_id
        FROM datasets d
        WHERE rad.dataset_id = d.id
        """
    )
    op.alter_column("role_assignments_dataset", "data_product_id", nullable=False)
    op.create_foreign_key(
        "fk_role_assignments_dataset_data_product_id",
        "role_assignments_dataset",
        "data_products",
        ["data_product_id"],
        ["id"],
        ondelete="CASCADE",
    )


def downgrade() -> None:
    op.drop_constraint(
        "fk_role_assignments_dataset_data_product_id",
        "role_assignments_dataset",
        type_="foreignkey",
    )
    op.drop_column("role_assignments_dataset", "data_product_id")
