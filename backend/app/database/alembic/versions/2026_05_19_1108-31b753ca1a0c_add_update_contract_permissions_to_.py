"""Add update contract permissions to owner role

Revision ID: 31b753ca1a0c
Revises: 8aa8df18d6ff
Create Date: 2026-05-19 11:08:46.366949

"""

from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "31b753ca1a0c"
down_revision: Union[str, None] = "8aa8df18d6ff"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Action.OUTPUT_PORT__UPDATE_CONTRACT = 415
    # Scope.DATASET = 'dataset', Prototype.OWNER = 2
    op.execute(
        """
        UPDATE roles
        SET permissions = (
            SELECT ARRAY(SELECT DISTINCT unnest(permissions || ARRAY[415]) ORDER BY 1)
        )
        WHERE scope = 'dataset'
          AND prototype = 2
          AND NOT (permissions @> ARRAY[415])
        """
    )


def downgrade() -> None:
    # Remove Action.OUTPUT_PORT__UPDATE_CONTRACT (415) from the DATASET/OWNER role
    op.execute(
        """
        UPDATE roles
        SET permissions = (
            SELECT ARRAY(SELECT unnest(permissions) EXCEPT SELECT 415 ORDER BY 1)
        )
        WHERE scope = 'dataset'
          AND prototype = 2
          AND permissions @> ARRAY[415]
        """
    )
