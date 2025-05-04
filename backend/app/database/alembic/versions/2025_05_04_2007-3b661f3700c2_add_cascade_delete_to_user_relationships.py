"""Add cascade delete to user relationships

Revision ID: 3b661f3700c2
Revises: 886fc49acbda
Create Date: 2025-05-04 20:07:41.866956

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "3b661f3700c2"
down_revision: Union[str, None] = "886fc49acbda"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def _upgrade_assignments_table(table_name: str):
    op.drop_constraint(
        f"{table_name}_user_id_fkey",
        table_name,
        type_="foreignkey",
    )
    op.drop_constraint(
        f"{table_name}_requested_by_id_fkey",
        table_name,
        type_="foreignkey",
    )
    op.drop_constraint(
        f"{table_name}_decided_by_id_fkey",
        table_name,
        type_="foreignkey",
    )

    op.create_foreign_key(
        f"{table_name}_user_id_fkey",
        table_name,
        "users",
        ["user_id"],
        ["id"],
        ondelete="CASCADE",
    )
    op.create_foreign_key(
        f"{table_name}_requested_by_id_fkey",
        table_name,
        "users",
        ["requested_by_id"],
        ["id"],
        ondelete="CASCADE",
    )
    op.create_foreign_key(
        f"{table_name}_decided_by_id_fkey",
        table_name,
        "users",
        ["decided_by_id"],
        ["id"],
        ondelete="CASCADE",
    )

def _downgrade_assignments_table(table_name: str):
    op.drop_constraint(
        f"{table_name}_user_id_fkey",
        table_name,
        type_="foreignkey",
    )
    op.drop_constraint(
        f"{table_name}_requested_by_id_fkey",
        table_name,
        type_="foreignkey",
    )
    op.drop_constraint(
        f"{table_name}_decided_by_id_fkey",
        table_name,
        type_="foreignkey",
    )

    op.create_foreign_key(
        f"{table_name}_user_id_fkey",
        table_name,
        "users",
        ["user_id"],
        ["id"],
    )
    op.create_foreign_key(
        f"{table_name}_requested_by_id_fkey",
        table_name,
        "users",
        ["requested_by_id"],
        ["id"],
    )
    op.create_foreign_key(
        f"{table_name}_decided_by_id_fkey",
        table_name,
        "users",
        ["decided_by_id"],
        ["id"],
    )


def upgrade() -> None:
    for table in ["role_assignments_data_product", "role_assignments_dataset"]:
        _upgrade_assignments_table(table)

    op.drop_constraint(
        "data_product_memberships_user_id_fkey",
        "data_product_memberships",
        type_="foreignkey",
    )
    op.create_foreign_key(
        "data_product_memberships_user_id_fkey",
        "data_product_memberships",
        "users",
        ["user_id"],
        ["id"],
        ondelete="CASCADE",
    )


def downgrade() -> None:
    for table in ["role_assignments_data_product", "role_assignments_dataset"]:
        _downgrade_assignments_table(table)

    op.drop_constraint(
        "data_product_memberships_user_id_fkey",
        "data_product_memberships",
        type_="foreignkey",
    )
    op.create_foreign_key(
        "data_product_memberships_user_id_fkey",
        "data_product_memberships",
        "users",
        ["user_id"],
        ["id"],
    )
