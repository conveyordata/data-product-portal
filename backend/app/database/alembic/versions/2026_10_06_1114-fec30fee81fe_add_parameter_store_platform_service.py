"""add parameter store platform service

Revision ID: fec30fee81fe
Revises: abd4229ea6af
Create Date: 2026-10-06 11:14:23.434594

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "fec30fee81fe"
down_revision: Union[str, None] = "abd4229ea6af"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        sa.text(
            """
            INSERT INTO platform_services (name, platform_id, result_string_template, technical_info_template)
            SELECT 'ParameterStore', p.id, '/{prefix}/{parameter_name}', '/{prefix}/{parameter_name}'
            FROM platforms AS p
            WHERE p.name = 'AWS'
            AND NOT EXISTS (SELECT 1 FROM platform_services WHERE name = 'ParameterStore')
            """
        )
    )


def downgrade() -> None:
    op.execute(
        sa.text(
            """
            WITH unused AS (
                SELECT ps.id FROM platform_services AS ps
                WHERE ps.name = 'ParameterStore'
                AND NOT EXISTS (SELECT 1 FROM data_outputs WHERE service_id = ps.id)
            ),
            env_configs AS (
                DELETE FROM env_platform_service_configs
                WHERE service_id IN (SELECT id FROM unused)
            ),
            configs AS (
                DELETE FROM platform_service_configs
                WHERE service_id IN (SELECT id FROM unused)
            )
            DELETE FROM platform_services WHERE id IN (SELECT id FROM unused)
            """
        )
    )
