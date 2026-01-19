"""store data quality summary for output ports

Revision ID: 7601ac14662a
Revises: ca5f5782790a
Create Date: 2026-01-19 15:23:46.910285

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

from app.data_products.output_ports.data_quality.enums import DataQualityStatus
from app.shared.model import utcnow

# revision identifiers, used by Alembic.
revision: str = "7601ac14662a"
down_revision: Union[str, None] = "ca5f5782790a"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "dataset_data_quality_summaries",
        sa.Column(
            "output_port_id",
            sa.UUID,
            sa.ForeignKey("datasets.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "id",
            sa.UUID,
            primary_key=True,
            nullable=False,
        ),
        sa.Column(
            "assets_with_checks",
            sa.SmallInteger(),
            primary_key=False,
            nullable=False,
            server_default="0",
        ),
        sa.Column(
            "assets_with_issues",
            sa.SmallInteger(),
            primary_key=False,
            nullable=False,
            server_default="0",
        ),
        sa.Column("details_url", sa.Text(), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("overall_status", sa.Enum(DataQualityStatus), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=utcnow(),
        ),
        sa.Column("dimensions", sa.JSON(), default={}),
    )

    op.create_table(
        "data_quality_technical_assets",
        sa.Column(
            "name",
            sa.Text(),
            nullable=False,
            primary_key=True,
        ),
        sa.Column(
            "status",
            sa.Enum(DataQualityStatus),
            nullable=False,
        ),
        sa.Column(
            "data_quality_summary_id",
            sa.UUID,
            sa.ForeignKey("dataset_data_quality_summaries.id", ondelete="CASCADE"),
            nullable=False,
            primary_key=True,
        ),
    )


def downgrade() -> None:
    op.drop_table("data_quality_technical_assets")
    op.drop_table("dataset_data_quality_summaries")
