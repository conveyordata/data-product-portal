"""Add create exploration to global role if it exists

Revision ID: 6449af439bdd
Revises: 63243c53dd67
Create Date: 2026-04-24 13:58:01.228045

"""

from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "6449af439bdd"
down_revision: Union[str, None] = "63243c53dd67"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Action.GLOBAL__CREATE_EXPLORATION = 108
    # Scope.GLOBAL = 'global', Prototype.EVERYONE = 1
    op.execute(
        """
        UPDATE roles
        SET permissions = (
            SELECT ARRAY(SELECT DISTINCT unnest(permissions || ARRAY[108]) ORDER BY 1)
        )
        WHERE scope = 'global'
          AND prototype = 1
          AND NOT (permissions @> ARRAY[108])
        """
    )


def downgrade() -> None:
    # Remove Action.GLOBAL__CREATE_EXPLORATION (108) from the GLOBAL/EVERYONE role
    op.execute(
        """
        UPDATE roles
        SET permissions = (
            SELECT ARRAY(SELECT unnest(permissions) EXCEPT SELECT 108 ORDER BY 1)
        )
        WHERE scope = 'global'
          AND prototype = 1
          AND permissions @> ARRAY[108]
        """
    )
