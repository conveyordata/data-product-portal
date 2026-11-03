"""Move create output port permission from global to data product scope

Revision ID: 7b1e4d2c9a05
Revises: a9203b7e41cd
Create Date: 2026-10-30 12:00:00.000000

"""

from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "7b1e4d2c9a05"
down_revision: Union[str, None] = "a9203b7e41cd"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        """
        UPDATE roles
        SET permissions = array_remove(permissions, 103)
        WHERE permissions @> ARRAY[103]
        """
    )
    op.execute(
        """
        UPDATE roles
        SET permissions = permissions || ARRAY[316]
        WHERE scope = 'data_product'
          AND permissions @> ARRAY[309]
          AND NOT (permissions @> ARRAY[316])
        """
    )


def downgrade() -> None:
    op.execute(
        """
        UPDATE roles
        SET permissions = array_remove(permissions, 316)
        WHERE permissions @> ARRAY[316]
        """
    )
    op.execute(
        """
        UPDATE roles
        SET permissions = permissions || ARRAY[103]
        WHERE scope = 'global'
          AND prototype = 1
          AND NOT (permissions @> ARRAY[103])
        """
    )
