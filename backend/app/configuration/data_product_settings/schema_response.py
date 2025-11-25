from typing import Optional, Sequence
from uuid import UUID

from app.configuration.data_product_settings.enums import (
    DataProductSettingScope,
    DataProductSettingType,
)
from app.configuration.data_product_settings.schema import DataProductSetting
from app.shared.schema import ORMModel


class BaseDataProductSettingGet(ORMModel):
    id: UUID
    category: str
    type: DataProductSettingType
    tooltip: str
    namespace: str
    name: str
    default: str
    order: int = 100
    scope: DataProductSettingScope


class DataProductSettingGet(BaseDataProductSettingGet):
    pass


class DataProductSettingsGetItem(BaseDataProductSettingGet):
    pass


class DataProductSettingsGet(ORMModel):
    data_product_settings: Sequence[DataProductSettingsGetItem]


class BaseDataProductSettingValueGet(ORMModel):
    id: UUID
    data_product_id: Optional[UUID] = None
    dataset_id: Optional[UUID] = None
    data_product_setting_id: UUID
    value: str

    # Nested schemas
    data_product_setting: DataProductSetting


class DataProductSettingValueGet(BaseDataProductSettingValueGet):
    pass


class DataProductSettingValuesGet(BaseDataProductSettingValueGet):
    pass


class UpdateDataProductSettingResponse(ORMModel):
    id: UUID


class CreateDataProductSettingResponse(ORMModel):
    id: UUID
