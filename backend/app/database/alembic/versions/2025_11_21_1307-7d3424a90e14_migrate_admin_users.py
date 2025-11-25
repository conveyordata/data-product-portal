"""Migrate admin users

Revision ID: 7d3424a90e14
Revises: 749165238a8f
Create Date: 2025-11-21 13:07:08.178869

"""

from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "7d3424a90e14"
down_revision: Union[str, None] = "749165238a8f"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Make them can_become_admin
    op.execute(
        """
        UPDATE users
        SET can_become_admin = TRUE,
            admin_expiry = NULL
        WHERE id IN (
            SELECT user_id FROM role_assignments_global
            WHERE role_id = (
                SELECT id FROM roles WHERE prototype = 3
            )
            AND email != 'systemaccount@noreply.com'
        )
        """
    )

    # Remove users with global role 'admin'
    op.execute(
        """
        DELETE FROM role_assignments_global
        WHERE role_id = (
            SELECT id FROM roles WHERE prototype = 3
        ) and user_id NOT IN (
            SELECT id FROM users WHERE email = 'systemaccount@noreply.com')
        """
    )


def downgrade() -> None:
    # Revert can_become_admin and admin_expiry
    op.execute(
        """
        INSERT INTO role_assignments_global (id, user_id, role_id, decision)
        SELECT gen_random_uuid(), id, (
            SELECT id FROM roles WHERE prototype = 3
        ), 'APPROVED'
        FROM users
        WHERE can_become_admin = TRUE
        """
    )
    op.execute(
        """
        UPDATE users
        SET can_become_admin = FALSE,
            admin_expiry = NULL
        WHERE can_become_admin = TRUE
        """
    )
