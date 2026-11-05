from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

from app.shared.model import utcnow

revision: str = "postgresql_0002_environment"
down_revision: Union[str, None] = "postgresql_0001_baseline"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = "d7b8c9e0f123"

TABLE = "postgresql_environment_configurations"


def upgrade() -> None:
    op.create_table(
        TABLE,
        sa.Column(
            "configuration_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("data_output_configurations.id", ondelete="CASCADE"),
            primary_key=True,
        ),
        sa.Column(
            "environment_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("environments.id", ondelete="CASCADE"),
            primary_key=True,
        ),
        sa.Column("engine_version", sa.String(), nullable=False),
        sa.Column("size", sa.String(), nullable=False),
        sa.Column("storage_gb", sa.Integer(), nullable=False),
        sa.Column("instance_name", sa.String(), nullable=False),
        sa.Column("created_on", sa.DateTime(timezone=False), server_default=utcnow()),
        sa.Column("updated_on", sa.DateTime(timezone=False), onupdate=utcnow()),
        sa.Column("deleted_at", sa.DateTime(timezone=False), nullable=True),
        if_not_exists=True,
    )
    op.execute(
        sa.text(
            """
            INSERT INTO postgresql_environment_configurations
                (configuration_id, environment_id, engine_version, size, storage_gb, instance_name)
            SELECT
                c.id,
                dpe.environment_id,
                CASE WHEN e.acronym = 'prd' THEN '16' ELSE '17' END,
                CASE WHEN e.acronym = 'prd' THEN 'medium' ELSE 'small' END,
                CASE WHEN e.acronym = 'prd' THEN 50 ELSE 20 END,
                left(CASE WHEN lower(p.database) ~ '^[a-z]' THEN '' ELSE 'pg-' END || left(regexp_replace(lower(p.database), '[^a-z0-9-]', '-', 'g'), 40) || '-' || left(p.id::text, 8) || CASE WHEN e.acronym = 'prd' THEN '' ELSE '-' || e.acronym END, 63)
            FROM data_output_configurations c
            JOIN postgresql_technical_asset_configurations p ON p.id = c.id
            JOIN data_outputs d ON d.configuration_id = c.id
            JOIN data_product_environments dpe ON dpe.data_product_id = d.owner_id
            JOIN environments e ON e.id = dpe.environment_id
            WHERE c.configuration_type = 'PostgreSQLTechnicalAssetConfiguration'
            ON CONFLICT DO NOTHING
            """
        )
    )


def downgrade() -> None:
    op.drop_table(TABLE, if_exists=True)
