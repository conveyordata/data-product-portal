from uuid import UUID
from warnings import deprecated

from app.configuration.data_product_settings.enums import (
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


class BaseValue(ORMModel):
    id: UUID
    data_product_setting_id: UUID
    value: str

    # Nested schemas
    data_product_setting: DataProductSetting


class DataProductSettingValue(BaseValue):
    data_product_id: UUID


class OutputPortSettingValue(BaseValue):
    output_port_id: UUID


@deprecated("Use OutputPortSettingValue instead")
class DatasetSettingValue(BaseValue):
    dataset_id: UUID

    def convert(self) -> OutputPortSettingValue:
        return OutputPortSettingValue(
            **self.model_dump(exclude={"dataset_id"}), output_port_id=self.dataset_id
        )
