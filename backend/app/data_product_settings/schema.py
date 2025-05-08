from typing import Optional
from uuid import UUID

from app.data_product_settings.enums import (
    DataProductSettingScope,
    DataProductSettingType,
)
from app.shared.schema import ORMModel


class DataProductSetting(ORMModel):
    id: UUID
    category: str
    type: DataProductSettingType
    tooltip: str
    namespace: str
    name: str
    default: str
    order: int = 100
    scope: DataProductSettingScope


class DataProductSettingValue(ORMModel):
    id: UUID
    data_product_id: Optional[UUID] = None
    dataset_id: Optional[UUID] = None
    data_product_setting_id: UUID
    value: str

    # Nested schemas
    data_product_setting: DataProductSetting
