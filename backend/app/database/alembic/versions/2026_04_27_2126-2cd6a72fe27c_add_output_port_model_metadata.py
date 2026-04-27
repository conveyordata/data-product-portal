"""add_output_port_model_metadata

Revision ID: 2cd6a72fe27c
Revises: a2b3c4d5e6f7
Create Date: 2026-04-27 21:26:38.735783

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

from app.shared.model import utcnow

revision: str = "2cd6a72fe27c"
down_revision: Union[str, None] = "a2b3c4d5e6f7"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "output_port_table_schemas",
        sa.Column("id", sa.UUID(), primary_key=True, nullable=False),
        sa.Column(
            "output_port_id",
            sa.UUID(),
            sa.ForeignKey("datasets.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("description", sa.String(), nullable=True),
    )
    op.create_index(
        op.f("ix_output_port_table_schemas_output_port_id"),
        "output_port_table_schemas",
        ["output_port_id"],
        unique=False,
    )

    op.create_table(
        "output_port_columns",
        sa.Column("id", sa.UUID(), primary_key=True, nullable=False),
        sa.Column(
            "table_schema_id",
            sa.UUID(),
            sa.ForeignKey("output_port_table_schemas.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("description", sa.String(), nullable=True),
        sa.Column("data_type", sa.String(), nullable=True),
    )

    op.create_table(
        "tags_output_port_table_schemas",
        sa.Column(
            "table_schema_id",
            sa.UUID(),
            sa.ForeignKey("output_port_table_schemas.id"),
            nullable=False,
        ),
        sa.Column("tag_id", sa.UUID(), sa.ForeignKey("tags.id"), nullable=False),
        sa.Column("created_on", sa.DateTime(timezone=False), server_default=utcnow()),
        sa.Column("updated_on", sa.DateTime(timezone=False), onupdate=utcnow()),
    )

    op.create_table(
        "tags_output_port_columns",
        sa.Column(
            "column_id",
            sa.UUID(),
            sa.ForeignKey("output_port_columns.id"),
            nullable=False,
        ),
        sa.Column("tag_id", sa.UUID(), sa.ForeignKey("tags.id"), nullable=False),
        sa.Column("created_on", sa.DateTime(timezone=False), server_default=utcnow()),
        sa.Column("updated_on", sa.DateTime(timezone=False), onupdate=utcnow()),
    )

    op.create_table(
        "output_port_semantic_models",
        sa.Column("id", sa.UUID(), primary_key=True, nullable=False),
        sa.Column(
            "output_port_id",
            sa.UUID(),
            sa.ForeignKey("datasets.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column(
            "format",
            sa.Enum(
                "MetricsFlow", "OpenSemanticInterchange", name="semanticmodelformat"
            ),
            nullable=False,
        ),
        sa.Column("content", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
    )
    op.create_index(
        op.f("ix_output_port_semantic_models_output_port_id"),
        "output_port_semantic_models",
        ["output_port_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        op.f("ix_output_port_semantic_models_output_port_id"),
        table_name="output_port_semantic_models",
    )
    op.drop_table("output_port_semantic_models")
    op.drop_table("tags_output_port_columns")
    op.drop_table("tags_output_port_table_schemas")
    op.drop_table("output_port_columns")
    op.drop_index(
        op.f("ix_output_port_table_schemas_output_port_id"),
        table_name="output_port_table_schemas",
    )
    op.drop_table("output_port_table_schemas")
