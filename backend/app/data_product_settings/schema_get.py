from typing import Optional
from uuid import UUID

from app.data_product_settings.enums import (
    DataProductSettingScope,
    DataProductSettingType,
)
from app.data_product_settings.schema_basic import DataProductSettingBasic
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


class DataProductSettingsGet(BaseDataProductSettingGet):
    pass


class BaseDataProductSettingValueGet(ORMModel):
    id: UUID
    data_product_id: Optional[UUID] = None
    dataset_id: Optional[UUID] = None
    data_product_setting_id: UUID
    value: str

    # Nested schemas
    data_product_setting: DataProductSettingBasic


class DataProductSettingValueGet(BaseDataProductSettingValueGet):
    pass


class DataProductSettingValuesGet(BaseDataProductSettingValueGet):
    pass
