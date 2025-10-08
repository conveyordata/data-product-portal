"""add data_product_id to dataset

Revision ID: d56d796fb20d
Revises: 0358e660a680
Create Date: 2025-10-03 12:51:14.866274

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "d56d796fb20d"
down_revision: Union[str, None] = "0358e660a680"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("datasets", sa.Column("data_product_id", sa.Uuid(), nullable=True))
    op.add_column("datasets", sa.Column("not_valid", sa.Boolean))
    op.create_foreign_key(
        "fk_datasets_data_product_id_data_products",
        "datasets",
        "data_products",
        ["data_product_id"],
        ["id"],
    )
    # set data_product_id by default to the owner_id of the first data_output_link
    op.execute(
        """
        UPDATE datasets
        SET data_product_id = (
            SELECT dos.owner_id
            FROM data_outputs_datasets dod
            JOIN data_outputs dos ON dod.data_output_id = dos.id
            WHERE dod.dataset_id = datasets.id
            ORDER BY dod.requested_on ASC
            LIMIT 1
        )
        WHERE data_product_id IS NULL
    """
    )
    # set not_valid to True if there are multiple different owner_ids
    # in data_output_links or if data_product_id is NULL
    op.execute(
        """
        UPDATE datasets
        SET not_valid = TRUE
        WHERE id IN (
            SELECT dataset_id
            FROM data_outputs_datasets dod
            JOIN data_outputs dos ON dod.data_output_id = dos.id
            GROUP BY dataset_id
            HAVING COUNT(DISTINCT dos.owner_id) > 1
        ) OR data_product_id IS NULL
    """
    )


def downgrade() -> None:
    op.drop_constraint(
        "fk_datasets_data_product_id_data_products", "datasets", type_="foreignkey"
    )
    op.drop_column("datasets", "data_product_id")
    op.drop_column("datasets", "not_valid")
