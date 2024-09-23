"""add updated on platform_services

Revision ID: 4f302694e90a
Revises: c6554418a88d
Create Date: 2024-09-20 15:55:34.667681

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy import orm

from app.platform_services.model import PlatformService
from app.platforms.model import Platform
from app.shared.model import utcnow

# revision identifiers, used by Alembic.
revision: str = "4f302694e90a"
down_revision: Union[str, None] = "c6554418a88d"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "platform_services",
        sa.Column("created_on", sa.DateTime(timezone=False), server_default=utcnow()),
    )
    op.add_column(
        "platform_services",
        sa.Column("updated_on", sa.DateTime(timezone=False), onupdate=utcnow()),
    )
    op.add_column("platform_services", sa.Column("deleted_at", sa.DateTime))

    # Adding initial data
    bind = op.get_bind()
    session = orm.Session(bind=bind)

    platform = Platform(name="AWS")
    platform.services = [PlatformService(name="S3"), PlatformService(name="Glue")]
    session.add(platform)
    session.commit()


def downgrade() -> None:
    op.drop_column("platform_services", "created_on")
    op.drop_column("platform_services", "updated_on")
    op.drop_column("platform_services", "deleted_on")
