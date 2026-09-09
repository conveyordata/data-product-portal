"""
ADR-0024's chosen storage shapes:
  - one shared, flexible JSONB column for a technical asset's own values
    (instead of a dedicated table per plugin type)
  - one shared, flexible JSONB column per (plugin, environment) for
    per-environment infrastructure details (instead of the
    platforms/platform_services/env_platform_configs/env_platform_service_configs
    tables)
"""

import uuid

from sqlalchemy import Column, ForeignKey, String
from sqlalchemy.dialects.postgresql import JSONB, UUID

from app.database.database import Base
from app.shared.model import BaseORM


class SpikeTechnicalAsset(Base, BaseORM):
    __tablename__ = "spike_technical_assets"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    data_product_id = Column(
        UUID(as_uuid=True),
        ForeignKey("data_products.id", ondelete="CASCADE"),
        nullable=False,
    )
    plugin_key = Column(String, nullable=False)
    config = Column(JSONB, nullable=False)


class SpikeEnvironmentConfig(Base, BaseORM):
    __tablename__ = "spike_environment_configs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    plugin_key = Column(String, nullable=False)
    environment_id = Column(
        UUID(as_uuid=True),
        ForeignKey("environments.id", ondelete="CASCADE"),
        nullable=False,
    )
    config = Column(JSONB, nullable=False)
