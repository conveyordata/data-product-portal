from typing import Sequence, Union

from alembic import op

revision: str = "6441623a586b"
down_revision: Union[str, None] = "7727032896e7"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        """
        INSERT INTO role_assignments_global (
            id,
            user_id,
            role_id,
            decision,
            requested_by_id,
            requested_on,
            decided_by_id,
            decided_on
        )
        SELECT
            gen_random_uuid(),
            users.id,
            '00000000-0000-0000-0000-000000000000'::uuid,
            'APPROVED',
            users.id,
            NOW(),
            users.id,
            NOW()
        FROM users
        WHERE users.email = 'systemaccount@noreply.com'
          AND NOT EXISTS (
              SELECT 1
              FROM role_assignments_global
              WHERE role_assignments_global.user_id = users.id
          )
        """
    )


def downgrade() -> None:
    op.execute(
        """
        DELETE FROM role_assignments_global
        WHERE user_id = (
            SELECT id
            FROM users
            WHERE email = 'systemaccount@noreply.com'
        )
          AND role_id = '00000000-0000-0000-0000-000000000000'::uuid
        """
    )
