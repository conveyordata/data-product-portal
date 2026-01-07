from enum import Enum
from typing import Optional, Sequence

from app.configuration.environments.platform_service_configurations.schema_response import (
    ConfigType,
)
from app.data_output_configuration.data_output_types import DataOutputTypes
from app.shared.schema import ORMModel


class UIElementType(str, Enum):
    String = "string"
    Select = "select"
    Checkbox = "checkbox"


class UIElementMetadata(ORMModel):
    label: str
    type: UIElementType
    required: bool
    name: str
    tooltip: Optional[str] = None
    options: Optional[dict] = None
    hidden: Optional[bool] = None
    pattern: Optional[str] = None
    initial_value: Optional[str | int | float | bool] = None
    value_prop_name: Optional[str] = None
    depends_on: Optional[dict] = None  # {"fieldName": str, "value": any}
    select_mode: Optional[str] = None  # "tags", "multiple", None
    max_count: Optional[int] = None
    disabled: Optional[bool] = None
    use_namespace_when_not_source_aligned: Optional[bool] = None
    normalize_array: Optional[bool] = None


class BaseDataOutputConfiguration(ORMModel):
    configuration_type: DataOutputTypes

    def render_template(self, template: str, **context) -> str:
        return template.format(**self.model_dump(), **context)

    def get_configuration(self, configs: list[ConfigType]) -> Optional[ConfigType]:
        raise NotImplementedError

    @classmethod
    def get_UI_metadata(cls) -> Sequence[UIElementMetadata]:
        return []

    def get_logo(self) -> str:
        return f"{self.__class__.__name__.removesuffix('DataOutput')}-logo.svg"
