"""migrate role assignments to identities

Revision ID: 18fb80f18c7d
Revises: 1d1b811732f3
Create Date: 2026-09-07 13:15:07.543858
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "18fb80f18c7d"
down_revision: Union[str, None] = "1d1b811732f3"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_constraint(
        "role_assignments_global_user_id_fkey",
        "role_assignments_global",
        type_="foreignkey",
    )
    op.alter_column(
        "role_assignments_global",
        "user_id",
        new_column_name="identity_id",
        existing_type=sa.UUID(),
        existing_nullable=False,
    )
    op.create_foreign_key(
        "role_assignments_global_identity_id_fkey",
        "role_assignments_global",
        "identities",
        ["identity_id"],
        ["id"],
    )

    op.drop_constraint(
        "role_assignments_data_product_user_id_fkey",
        "role_assignments_data_product",
        type_="foreignkey",
    )
    op.alter_column(
        "role_assignments_data_product",
        "user_id",
        new_column_name="identity_id",
        existing_type=sa.UUID(),
        existing_nullable=False,
    )
    op.create_foreign_key(
        "role_assignments_data_product_identity_id_fkey",
        "role_assignments_data_product",
        "identities",
        ["identity_id"],
        ["id"],
    )


def downgrade() -> None:
    op.execute(
        """
        DO $$
        BEGIN
            IF EXISTS (
                SELECT identity_id FROM role_assignments_global
                EXCEPT
                SELECT id FROM users
            ) OR EXISTS (
                SELECT identity_id FROM role_assignments_data_product
                EXCEPT
                SELECT id FROM users
            ) THEN
                RAISE EXCEPTION
                    'Cannot downgrade while non-user role assignments exist';
            END IF;
        END
        $$;
        """
    )

    op.drop_constraint(
        "role_assignments_data_product_identity_id_fkey",
        "role_assignments_data_product",
        type_="foreignkey",
    )
    op.alter_column(
        "role_assignments_data_product",
        "identity_id",
        new_column_name="user_id",
        existing_type=sa.UUID(),
        existing_nullable=False,
    )
    op.create_foreign_key(
        "role_assignments_data_product_user_id_fkey",
        "role_assignments_data_product",
        "users",
        ["user_id"],
        ["id"],
    )

    op.drop_constraint(
        "role_assignments_global_identity_id_fkey",
        "role_assignments_global",
        type_="foreignkey",
    )
    op.alter_column(
        "role_assignments_global",
        "identity_id",
        new_column_name="user_id",
        existing_type=sa.UUID(),
        existing_nullable=False,
    )
    op.create_foreign_key(
        "role_assignments_global_user_id_fkey",
        "role_assignments_global",
        "users",
        ["user_id"],
        ["id"],
    )
