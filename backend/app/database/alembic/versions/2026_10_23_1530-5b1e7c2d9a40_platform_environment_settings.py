"""Replace platform and platform service configuration with platform environment settings

Revision ID: 5b1e7c2d9a40
Revises: 3f9c2a7d1e04
Create Date: 2026-10-23 15:30:00.000000

"""

import json
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

from app.shared.model import utcnow

revision: str = "5b1e7c2d9a40"
down_revision: Union[str, None] = "3f9c2a7d1e04"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    settings_table = op.create_table(
        "platform_environment_settings",
        sa.Column("platform_key", sa.String, primary_key=True),
        sa.Column(
            "environment_id",
            sa.UUID,
            sa.ForeignKey("environments.id", ondelete="CASCADE"),
            primary_key=True,
        ),
        sa.Column("settings", postgresql.JSONB, nullable=False),
        sa.Column("created_on", sa.DateTime, server_default=utcnow()),
        sa.Column("updated_on", sa.DateTime, onupdate=utcnow()),
    )

    connection = op.get_bind()
    settings: dict[tuple[str, str], dict] = {}
    for platform, environment_id, config in connection.execute(
        sa.text(
            "SELECT p.name, c.environment_id, c.config FROM env_platform_configs c "
            "JOIN platforms p ON p.id = c.platform_id"
        )
    ):
        settings.setdefault((platform.lower(), environment_id), {}).update(
            json.loads(config)
        )
    for platform, service, environment_id, config in connection.execute(
        sa.text(
            "SELECT p.name, s.name, c.environment_id, c.config "
            "FROM env_platform_service_configs c "
            "JOIN platforms p ON p.id = c.platform_id "
            "JOIN platform_services s ON s.id = c.service_id"
        )
    ):
        settings.setdefault((platform.lower(), environment_id), {})[
            service.lower().replace("-", "_")
        ] = json.loads(config)
    if settings:
        op.bulk_insert(
            settings_table,
            [
                {"platform_key": key, "environment_id": env_id, "settings": value}
                for (key, env_id), value in settings.items()
            ],
        )

    op.drop_column("data_outputs", "platform_id")
    op.drop_column("data_outputs", "service_id")
    op.drop_table("env_platform_service_configs")
    op.drop_table("env_platform_configs")
    op.drop_table("platform_service_configs")
    op.drop_table("platform_services")
    op.drop_table("platforms")


def downgrade() -> None:
    raise NotImplementedError("Prototype migration has no downgrade")
