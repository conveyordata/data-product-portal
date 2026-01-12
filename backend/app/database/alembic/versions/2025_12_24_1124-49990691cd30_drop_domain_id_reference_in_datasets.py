"""drop domain_id reference in datasets

Revision ID: 49990691cd30
Revises: b3f7df8cf884
Create Date: 2025-12-24 11:24:57.790192

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "49990691cd30"
down_revision: Union[str, None] = "b3f7df8cf884"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_column(
        "datasets",
        "domain_id",
    )


def downgrade() -> None:
    op.add_column(
        "datasets",
        sa.Column("domain_id", sa.UUID, nullable=True),
    )

    op.execute(
        """
        UPDATE datasets
        SET domain_id = (SELECT dp.domain_id
                               FROM data_products dp
                               WHERE dp.id = datasets.data_product_id
            LIMIT 1
            )
        """
    )
