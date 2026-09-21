"""Postgres output port plugin

Revision ID: 491c8783a7bc
Revises: 638303a2cb77
Create Date: 2026-03-02 14:54:51.833214

"""

from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "491c8783a7bc"
down_revision: Union[str, None] = "638303a2cb77"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # The postgresql plugin's own versions/ now owns its table; this migration
    # only renames the discriminator on the shared base table.
    op.execute(
        """
        UPDATE data_output_configurations
        SET configuration_type = 'PostgreSQLTechnicalAssetConfiguration'
        WHERE configuration_type = 'PostgreSQLDataOutput'
        """
    )


def downgrade() -> None:
    op.execute(
        """
        UPDATE data_output_configurations
        SET configuration_type = 'PostgreSQLDataOutput'
        WHERE configuration_type = 'PostgreSQLTechnicalAssetConfiguration'
        """
    )
