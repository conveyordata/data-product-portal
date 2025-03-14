from typing import Optional
from uuid import UUID

from pydantic import Field

from app.data_product_settings.enums import (
    DataProductSettingScope,
    DataProductSettingType,
)
from app.data_product_settings.model import (
    DataProductSetting as DataProductSettingModel,
)
from app.data_product_settings.model import (
    DataProductSettingValue as DataProductSettingValueModel,
)
from app.shared.schema import ORMModel


class DataProductSettingCreate(ORMModel):
    category: str = Field(..., description="Category of the data product setting")
    type: DataProductSettingType = Field(
        ..., description="Type of the data product setting"
    )
    tooltip: str = Field(..., description="Tooltip for the data product setting")
    external_id: str = Field(
        ..., description="External identifier for the data product setting"
    )
    name: str = Field(..., description="Name of the data product setting")
    default: str = Field(..., description="Default value of the data product setting")
    order: int = Field(100, description="Order of the data product setting")
    scope: DataProductSettingScope = Field(
        ..., description="Scope of the data product setting"
    )

    class Meta:
        orm_model = DataProductSettingModel


class DataProductSettingUpdate(DataProductSettingCreate):
    pass


class DataProductSetting(DataProductSettingCreate):
    id: UUID = Field(..., description="Unique identifier for the data product setting")


class DataProductSettingValueCreate(ORMModel):
    data_product_id: Optional[UUID] = Field(
        None, description="Unique identifier of the data product, if applicable"
    )
    dataset_id: Optional[UUID] = Field(
        None, description="Unique identifier of the dataset, if applicable"
    )
    data_product_setting_id: UUID = Field(
        ..., description="Unique identifier of the data product setting"
    )
    value: str = Field(..., description="Value of the data product setting")

    class Meta:
        orm_model = DataProductSettingValueModel


class DataProductSettingValue(DataProductSettingValueCreate):
    id: UUID = Field(
        ..., description="Unique identifier for the data product setting value"
    )
    data_product_setting: DataProductSetting = Field(
        ..., description="Data product setting associated with the value"
    )
