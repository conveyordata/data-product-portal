"""Add Settings related tables

Revision ID: 45016ec9a7b7
Revises: 2e48ad16e9f7
Create Date: 2024-07-29 13:45:09.823621

"""

from enum import StrEnum
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy import orm

from app.platform_services.model import PlatformService
from app.platforms.model import Platform
from app.shared.model import utcnow

# revision identifiers, used by Alembic.
revision: str = "45016ec9a7b7"
down_revision: Union[str, None] = "fad6a9c64d60"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_table("platforms")
    op.execute("DROP TYPE platformtypes;")

    op.create_table(
        "platforms",
        sa.Column(
            "id", sa.UUID, primary_key=True, server_default=sa.text("gen_random_uuid()")
        ),
        sa.Column("name", sa.String, unique=True, nullable=False),
    )

    op.create_table(
        "platform_services",
        sa.Column(
            "id", sa.UUID, primary_key=True, server_default=sa.text("gen_random_uuid()")
        ),
        sa.Column("name", sa.String, nullable=False),
        sa.Column("platform_id", sa.UUID, sa.ForeignKey("platforms.id")),
    )

    op.create_table(
        "platform_service_configs",
        sa.Column(
            "id", sa.UUID, primary_key=True, server_default=sa.text("gen_random_uuid()")
        ),
        sa.Column("platform_id", sa.UUID, sa.ForeignKey("platforms.id")),
        sa.Column("service_id", sa.UUID, sa.ForeignKey("platform_services.id")),
        sa.Column("config", sa.String),
        sa.Column("created_on", sa.DateTime(timezone=False), server_default=utcnow()),
        sa.Column("updated_on", sa.DateTime(timezone=False), onupdate=utcnow()),
        sa.Column("deleted_at", sa.DateTime),
    )

    op.create_table(
        "env_platform_service_configs",
        sa.Column(
            "id", sa.UUID, primary_key=True, server_default=sa.text("gen_random_uuid()")
        ),
        sa.Column("platform_id", sa.UUID, sa.ForeignKey("platforms.id")),
        sa.Column("service_id", sa.UUID, sa.ForeignKey("platform_services.id")),
        sa.Column("environment", sa.String, sa.ForeignKey("environments.name")),
        sa.Column("config", sa.String),
        sa.Column("created_on", sa.DateTime(timezone=False), server_default=utcnow()),
        sa.Column("updated_on", sa.DateTime(timezone=False), onupdate=utcnow()),
        sa.Column("deleted_at", sa.DateTime),
    )

    # Adding initial data
    bind = op.get_bind()
    session = orm.Session(bind=bind)

    platform = Platform(name="AWS")
    platform.services = [PlatformService(name="S3"), PlatformService(name="Glue")]
    session.add(platform)
    session.commit()


def downgrade() -> None:
    class PlatformTypes(StrEnum):
        AWS = "AWS"

    op.drop_table("env_platform_service_configs")
    op.drop_table("platform_service_configs")
    op.drop_table("platform_services")
    op.drop_table("platforms")

    op.create_table(
        "platforms",
        sa.Column(
            "id", sa.UUID, primary_key=True, server_default=sa.text("gen_random_uuid()")
        ),
        sa.Column("name", sa.Enum(PlatformTypes)),
        sa.Column("settings", sa.String),
        sa.Column("environment", sa.String, sa.ForeignKey("environments.name")),
        sa.Column("created_on", sa.DateTime(timezone=False), server_default=utcnow()),
        sa.Column("updated_on", sa.DateTime(timezone=False), onupdate=utcnow()),
        sa.Column("deleted_at", sa.DateTime),
    )
    op.create_unique_constraint(
        "uq_env_platform_deleted_at", "platforms", ["environment", "name", "deleted_at"]
    )
