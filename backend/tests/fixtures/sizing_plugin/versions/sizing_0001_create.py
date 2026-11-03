import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

from app.shared.model import utcnow

revision = "sizing_0001_create"
down_revision = None
branch_labels = None
depends_on = "d7b8c9e0f123"

CONFIGURATION_TABLE = "sizing_technical_asset_configurations"
ENVIRONMENT_TABLE = "sizing_configurations"


def upgrade() -> None:
    op.create_table(
        CONFIGURATION_TABLE,
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("data_output_configurations.id", ondelete="CASCADE"),
            primary_key=True,
        ),
        sa.Column("path", sa.String(), nullable=True),
        sa.Column("created_on", sa.DateTime(timezone=False), server_default=utcnow()),
        sa.Column("updated_on", sa.DateTime(timezone=False), onupdate=utcnow()),
        sa.Column("deleted_at", sa.DateTime(timezone=False), nullable=True),
    )
    op.create_table(
        ENVIRONMENT_TABLE,
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
        sa.Column("size", sa.String(), nullable=False),
        sa.Column("replicas", sa.Integer(), nullable=False),
        sa.Column("label", sa.String(), nullable=False),
        sa.Column("created_on", sa.DateTime(timezone=False), server_default=utcnow()),
        sa.Column("updated_on", sa.DateTime(timezone=False), onupdate=utcnow()),
        sa.Column("deleted_at", sa.DateTime(timezone=False), nullable=True),
    )


def downgrade() -> None:
    op.drop_table(ENVIRONMENT_TABLE)
    op.drop_table(CONFIGURATION_TABLE)
