from app.data_output_configuration.data_output_types import DataOutputTypes
from app.shared.schema import ORMModel


class BaseDataOutputConfiguration(ORMModel):
    configuration_type: DataOutputTypes
