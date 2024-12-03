from uuid import UUID

from app.data_product_settings.model import (
    DataProductSetting as DataProductSettingModel,
)
from app.shared.schema import ORMModel


class DataProductSettingCreate(ORMModel):
    divider: str
    type: str  # ENUM
    tooltip: str
    name: str

    class Meta:
        orm_model = DataProductSettingModel


class DataProductSetting(DataProductSettingCreate):
    id: UUID
