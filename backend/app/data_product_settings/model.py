import uuid
from typing import TYPE_CHECKING

from sqlalchemy import Column, Enum, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.data_product_settings.enums import (
    DataProductSettingScope,
    DataProductSettingType,
)
from app.database.database import Base
from app.shared.model import BaseORM

if TYPE_CHECKING:
    from app.datasets.model import Dataset
    from app.data_products.model import DataProduct


class DataProductSettingValue(Base, BaseORM):
    __tablename__ = "data_products_settings_values"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    value = Column(String)

    # Foreign keys
    data_product_setting_id: Mapped[UUID] = mapped_column(
        ForeignKey("data_product_settings.id")
    )
    data_product_id: Mapped[UUID] = mapped_column(
        ForeignKey("data_products.id"), nullable=True
    )
    dataset_id: Mapped[UUID] = mapped_column(ForeignKey("datasets.id"), nullable=True)

    # Relationships
    data_product_setting: Mapped["DataProductSetting"] = relationship(
        back_populates="data_product_setting_value",
        order_by="DataProductSetting.name",
        lazy="joined",
    )
    data_product: Mapped["DataProduct"] = relationship(
        back_populates="data_product_settings",
        order_by="DataProduct.name",
        lazy="raise",
    )
    dataset: Mapped["Dataset"] = relationship(
        back_populates="data_product_settings",
        order_by="Dataset.name",
        lazy="raise",
    )


class DataProductSetting(Base, BaseORM):
    __tablename__ = "data_product_settings"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    namespace = Column(String)
    name = Column(String)
    tooltip = Column(String)
    type = Column(Enum(DataProductSettingType))
    category = Column(String)
    default = Column(String)
    order = Column(Integer)
    scope = Column(Enum(DataProductSettingScope))

    # Relationships
    data_product_setting_value: Mapped[list["DataProductSettingValue"]] = relationship(
        back_populates="data_product_setting",
        cascade="all, delete-orphan",
        order_by="DataProductSettingValue.data_product_id",
        lazy="raise",
    )
