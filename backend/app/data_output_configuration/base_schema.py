from typing import Optional

from app.data_output_configuration.data_output_types import DataOutputTypes
from app.environment_platform_service_configurations.schema import ConfigType
from app.shared.schema import ORMModel


class BaseDataOutputConfiguration(ORMModel):
    configuration_type: DataOutputTypes

    def render_template(self, template: str, **context) -> str:
        return template.format(**self.model_dump(), **context)

    def get_configuration(self, configs: list[ConfigType]) -> Optional[ConfigType]:
        raise NotImplementedError
