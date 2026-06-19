"""lowercase status

Revision ID: a07fd336c073
Revises: f2fa245edde
Create Date: 2026-06-19 10:09:11.955460

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "a07fd336c073"
down_revision: Union[str, None] = "f2fa245edde"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        """
        UPDATE abstract_data_products
        SET status = LOWER(status)
        """
    )


def downgrade() -> None:
    op.execute(
        """
        UPDATE abstract_data_products
        SET status = UPPER(status)
        """
    )
