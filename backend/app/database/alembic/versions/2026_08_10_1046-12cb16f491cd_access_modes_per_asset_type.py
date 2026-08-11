"""Access modes per asset type

Revision ID: 12cb16f491cd
Revises: b15295e377ac
Create Date: 2026-08-10 10:46:49.910273

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "12cb16f491cd"
down_revision: Union[str, None] = "b15295e377ac"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_index("uq_access_modes_name", "access_modes", ["name"], unique=True)
    op.add_column(
        "access_modes",
        sa.Column(
            "technical_asset_types",
            postgresql.ARRAY(sa.Text()),
            nullable=True,
        ),
    )
    op.execute(
        """
        UPDATE access_modes
        SET technical_asset_types = access_mode_types.technical_asset_types
        FROM (
            SELECT
                technical_asset_access_modes.access_mode_id,
                array_agg(
                    DISTINCT data_output_configurations.configuration_type
                    ORDER BY data_output_configurations.configuration_type
                ) AS technical_asset_types
            FROM technical_asset_access_modes
            JOIN data_outputs
                ON data_outputs.id = technical_asset_access_modes.technical_asset_id
            JOIN data_output_configurations
                ON data_output_configurations.id = data_outputs.configuration_id
            GROUP BY technical_asset_access_modes.access_mode_id
        ) AS access_mode_types
        WHERE access_modes.id = access_mode_types.access_mode_id
        """
    )
    # We delete access modes without a type, as they are not valid anymore.
    # Should not happen since we haven't released this yet
    op.execute(
        """
        DELETE FROM access_modes
        WHERE technical_asset_types IS NULL OR cardinality(technical_asset_types) = 0
        """
    )
    op.alter_column("access_modes", "technical_asset_types", nullable=False)
    op.create_check_constraint(
        "ck_access_modes_technical_asset_types_non_empty",
        "access_modes",
        "cardinality(technical_asset_types) > 0",
    )


def downgrade() -> None:
    op.drop_constraint(
        "ck_access_modes_technical_asset_types_non_empty",
        "access_modes",
        type_="check",
    )
    op.drop_column("access_modes", "technical_asset_types")
    op.drop_index("uq_access_modes_name", table_name="access_modes")
