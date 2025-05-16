from app.data_output_configuration.data_output_types import DataOutputTypes
from app.shared.schema import ORMModel


class BaseDataOutputConfiguration(ORMModel):
    configuration_type: DataOutputTypes

    def output_result_string(self, template: str) -> str:
        return template.format(**self.model_dump())
