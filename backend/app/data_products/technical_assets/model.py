import uuid
from typing import TYPE_CHECKING, Optional

from fastapi import HTTPException, status
from sqlalchemy import Column, Enum, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, Session, relationship

from app.core.webhooks.events import TechnicalAssetEvent
from app.data_products.technical_assets.status import TechnicalAssetStatus
from app.database.event_mixin import EventTrackedMixin

if TYPE_CHECKING:
    from app.configuration.access_modes.model import AccessMode
    from app.configuration.platforms.model import PlatformEnvironmentSettings
    from app.data_products.model import DataProduct
    from app.data_products.output_port_technical_assets_link.model import (
        TechnicalAssetOutputPortAssociation,
    )
    from app.technical_asset_configuration.base_model import TechnicalAssetConfiguration

from app.configuration.tags.model import Tag, tag_technical_asset_table
from app.database.database import Base, ensure_exists
from app.shared.model import BaseORM


class TechnicalAssetAccessMode(Base, BaseORM):
    __tablename__ = "technical_asset_access_modes"

    technical_asset_id = Column(
        UUID(as_uuid=True), ForeignKey("data_outputs.id"), primary_key=True
    )
    access_mode_id = Column(
        UUID(as_uuid=True), ForeignKey("access_modes.id"), primary_key=True
    )


class TechnicalAsset(Base, BaseORM, EventTrackedMixin):
    __tablename__ = "data_outputs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    namespace = Column(String)
    name = Column(String)
    description = Column(String)
    status: TechnicalAssetStatus = Column(Enum(TechnicalAssetStatus))
    technical_mapping = Column(String)

    owner_id: Mapped[UUID] = Column(ForeignKey("data_products.id"))
    configuration_id: Mapped[UUID] = Column(ForeignKey("data_output_configurations.id"))

    owner: Mapped["DataProduct"] = relationship(
        back_populates="technical_assets", lazy="joined"
    )
    configuration: Mapped["TechnicalAssetConfiguration"] = relationship(lazy="joined")

    output_port_links: Mapped[list["TechnicalAssetOutputPortAssociation"]] = (
        relationship(
            "TechnicalAssetOutputPortAssociation",
            back_populates="technical_asset",
            cascade="all, delete-orphan",
            order_by="TechnicalAssetOutputPortAssociation.status.desc()",
            lazy="raise",
        )
    )
    tags: Mapped[list[Tag]] = relationship(
        secondary=tag_technical_asset_table,
        back_populates="technical_assets",
        lazy="selectin",
    )

    platform_settings: list["PlatformEnvironmentSettings"] = []
    access_modes: Mapped[list["AccessMode"]] = relationship(
        "AccessMode",
        secondary="technical_asset_access_modes",
        order_by="AccessMode.name",
        lazy="selectin",
    )

    def to_event(self) -> TechnicalAssetEvent:
        return TechnicalAssetEvent(
            id=self.id,
            data_product_id=self.owner_id,
        )


def ensure_technical_asset_exists(
    technical_asset_id: UUID,
    db: Session,
    data_product_id: Optional[UUID] = None,
    **kwargs,
) -> TechnicalAsset:
    asset: TechnicalAsset = ensure_exists(
        technical_asset_id, db, TechnicalAsset, **kwargs
    )
    if data_product_id is not None and asset.owner_id != data_product_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Required item {technical_asset_id} does not exist",
        )
    return asset
