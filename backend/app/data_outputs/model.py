import uuid
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, Column, Enum, ForeignKey, String, and_
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, foreign, relationship

from app.configuration.environments.platform_service_configurations.model import (
    EnvironmentPlatformServiceConfiguration,
)
from app.data_outputs.status import TechnicalAssetStatus

if TYPE_CHECKING:
    from app.configuration.platforms.model import Platform
    from app.configuration.platforms.platform_services.model import PlatformService
    from app.data_output_configuration.base_model import BaseDataOutputConfiguration
    from app.data_outputs_datasets.model import DataOutputDatasetAssociation
    from app.data_products.model import DataProduct

from app.configuration.tags.model import Tag, tag_data_output_table
from app.database.database import Base
from app.shared.model import BaseORM


class DataOutput(Base, BaseORM):
    __tablename__ = "data_outputs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    namespace = Column(String)
    name = Column(String)
    description = Column(String)
    status: TechnicalAssetStatus = Column(Enum(TechnicalAssetStatus))
    sourceAligned = Column(Boolean)

    # Foreign keys
    platform_id: Mapped[UUID] = Column(ForeignKey("platforms.id"))
    service_id: Mapped[UUID] = Column(ForeignKey("platform_services.id"))
    owner_id: Mapped[UUID] = Column(ForeignKey("data_products.id"))
    configuration_id: Mapped[UUID] = Column(ForeignKey("data_output_configurations.id"))

    # Relationships
    platform: Mapped["Platform"] = relationship(lazy="joined")
    service: Mapped["PlatformService"] = relationship(lazy="joined")
    owner: Mapped["DataProduct"] = relationship(
        back_populates="data_outputs", lazy="joined"
    )
    configuration: Mapped["BaseDataOutputConfiguration"] = relationship(lazy="joined")

    dataset_links: Mapped[list["DataOutputDatasetAssociation"]] = relationship(
        "DataOutputDatasetAssociation",
        back_populates="data_output",
        cascade="all, delete-orphan",
        order_by="DataOutputDatasetAssociation.status.desc()",
        lazy="raise",
    )
    tags: Mapped[list[Tag]] = relationship(
        secondary=tag_data_output_table, back_populates="data_outputs", lazy="joined"
    )

    environment_configurations: Mapped[
        list["EnvironmentPlatformServiceConfiguration"]
    ] = relationship(
        primaryjoin=and_(
            platform_id == foreign(EnvironmentPlatformServiceConfiguration.platform_id),
            service_id == foreign(EnvironmentPlatformServiceConfiguration.service_id),
        ),
        lazy="raise",
        viewonly=True,
    )
