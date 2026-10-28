"""Add output port permissions to data product owner

Revision ID: c8fbf0cf31e4
Revises: ae23301a4a69
Create Date: 2026-09-04 14:30:00.000000

"""

from typing import Sequence, Union

from alembic import op

revision: str = "c8fbf0cf31e4"
down_revision: Union[str, None] = "ae23301a4a69"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        """
        UPDATE roles
        SET permissions = (
            SELECT ARRAY(
                SELECT DISTINCT unnest(
                    permissions || ARRAY[
                        401, 402, 403, 404, 405, 406, 407, 408,
                        409, 410, 411, 412, 413, 414, 415
                    ]
                )
                ORDER BY 1
            )
        )
        WHERE scope = 'data_product'
          AND prototype = 2
        """
    )


def downgrade() -> None:
    op.execute(
        """
        UPDATE roles
        SET permissions = (
            SELECT ARRAY(
                SELECT unnest(permissions)
                EXCEPT SELECT unnest(
                    ARRAY[
                        401, 402, 403, 404, 405, 406, 407, 408,
                        409, 410, 411, 412, 413, 414, 415
                    ]
                )
                ORDER BY 1
            )
        )
        WHERE scope = 'data_product'
          AND prototype = 2
        """
    )
