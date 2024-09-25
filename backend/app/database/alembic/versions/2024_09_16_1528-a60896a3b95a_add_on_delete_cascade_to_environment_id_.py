"""Add ON DELETE CASCADE to environment_id foreign key

Revision ID: a60896a3b95a
Revises: 926e7e37f11e
Create Date: 2024-09-16 15:28:11.741125

"""

from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "a60896a3b95a"
down_revision: Union[str, None] = "926e7e37f11e"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    # Drop the old foreign key constraint
    op.drop_constraint(
        "env_platform_service_configs_environment_id_fkey",
        "env_platform_service_configs",
        type_="foreignkey",
    )

    # Create the new foreign key constraint with ON DELETE CASCADE
    op.create_foreign_key(
        "env_platform_service_configs_environment_id_fkey",
        "env_platform_service_configs",
        "environments",
        ["environment_id"],
        ["id"],
        ondelete="CASCADE",
    )


def downgrade():
    # Drop the cascade foreign key constraint
    op.drop_constraint(
        "env_platform_service_configs_environment_id_fkey",
        "env_platform_service_configs",
        type_="foreignkey",
    )

    # Re-create the original foreign key constraint without ON DELETE CASCADE
    op.create_foreign_key(
        "env_platform_service_configs_environment_id_fkey",
        "env_platform_service_configs",
        "environments",
        ["environment_id"],
        ["id"],
    )
