from uuid import UUID

from app.data_product_settings.enums import DataProductSettingType
from app.data_product_settings.model import (
    DataProductSetting as DataProductSettingModel,
)
from app.data_product_settings.model import (
    DataProductSettingValue as DataProductSettingValueModel,
)
from app.shared.schema import ORMModel


class DataProductSettingCreate(ORMModel):
    divider: str
    type: DataProductSettingType
    tooltip: str
    external_id: str
    name: str
    default: str
    order: int = 100

    class Meta:
        orm_model = DataProductSettingModel


class DataProductSetting(DataProductSettingCreate):
    id: UUID


class DataProductSettingValueCreate(ORMModel):
    data_product_id: UUID
    data_product_setting_id: UUID
    value: str

    class Meta:
        orm_model = DataProductSettingValueModel


class DataProductSettingValue(DataProductSettingValueCreate):
    id: UUID
    data_product_setting: DataProductSetting
