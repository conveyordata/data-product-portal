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
from app.datasets.model import Dataset
from app.shared.model import BaseORM

if TYPE_CHECKING:
    from app.data_products.model import DataProduct


class DataProductSettingValue(Base, BaseORM):
    __tablename__ = "data_products_settings_values"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    data_product_id: Mapped[uuid.UUID] = mapped_column(
        "data_product_id", ForeignKey("data_products.id"), nullable=True
    )
    data_product: Mapped["DataProduct"] = relationship(
        "DataProduct",
        back_populates="data_product_settings",
        order_by="DataProduct.name",
    )
    data_product_setting_id: Mapped[uuid.UUID] = mapped_column(
        "data_product_setting_id", ForeignKey("data_product_settings.id")
    )
    dataset_id: Mapped[uuid.UUID] = mapped_column(
        "dataset_id", ForeignKey("datasets.id"), nullable=True
    )
    dataset: Mapped["Dataset"] = relationship(
        "Dataset",
        back_populates="data_product_settings",
        order_by="Dataset.name",
    )
    data_product_setting: Mapped["DataProductSetting"] = relationship(
        "DataProductSetting",
        back_populates="data_products",
        order_by="DataProduct.name",
    )
    value = Column(String)


class DataProductSetting(Base, BaseORM):
    __tablename__ = "data_product_settings"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    external_id = Column(String)
    name = Column(String)
    tooltip = Column(String)
    type = Column(Enum(DataProductSettingType))
    category = Column(String)
    default = Column(String)
    order = Column(Integer)
    scope = Column(Enum(DataProductSettingScope))

    data_products: Mapped[list["DataProductSettingValue"]] = relationship(
        "DataProductSettingValue",
        back_populates="data_product_setting",
        cascade="all, delete-orphan",
        order_by="DataProductSettingValue.data_product_id",
    )
