"""Output Port query stats action and private output port refactor

Revision ID: ad035abcf21d
Revises: 6271ee228708
Create Date: 2026-09-02 10:17:33.779789

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "ad035abcf21d"
down_revision: Union[str, None] = "6271ee228708"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Action.OUTPUT_PORT__UPDATE_QUERY_STATS = 416
    # Scope.DATASET = 'dataset', Scope.DATA_PRODUCT = 'data_product', Prototype.OWNER = 2
    op.execute(
        """
        UPDATE roles
        SET permissions = (
            SELECT ARRAY(SELECT DISTINCT unnest(permissions || ARRAY[416]) ORDER BY 1)
        )
        WHERE (scope = 'dataset' or scope = 'data_product')
          AND prototype = 2
          AND NOT (permissions @> ARRAY[416])
        """
    )

    op.execute(
        sa.text(
            """
            UPDATE roles
            SET permissions = COALESCE(permissions, ARRAY[]::int[]) || :read_action
            WHERE scope = ANY(:scopes)
              AND NOT (:read_action = ANY(COALESCE(permissions, ARRAY[]::int[])))
            """
        ).bindparams(
            read_action=int(902),  # HIDDEN__OUTPUT_PORT_READ
            scopes=["dataset", "data_product"],  # Scope.DATASET and Scope.DATA_PRODUCT
        )
    )


def downgrade() -> None:
    # Remove Action.OUTPUT_PORT__UPDATE_QUERY_STATS (416) from the DATASET/OWNER role
    op.execute(
        """
        UPDATE roles
        SET permissions = (
            SELECT ARRAY(SELECT unnest(permissions) EXCEPT SELECT 416 ORDER BY 1)
        )
        WHERE (scope = 'dataset' or scope = 'data_product')
          AND prototype = 2
          AND permissions @> ARRAY[416]
        """
    )
    op.execute(
        sa.text(
            """
            UPDATE roles
            SET permissions = array_remove(permissions, :read_action)
            WHERE scope = ANY(:scopes)
            """
        ).bindparams(
            read_action=int(902),  # HIDDEN__OUTPUT_PORT_READ
            scopes=["dataset", "data_product"],  # Scope.DATASET and Scope.DATA_PRODUCT
        )
    )
