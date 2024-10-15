from app.data_outputs.data_output_types import DataOutputTypes
from app.shared.schema import ORMModel


class BaseDataOutputConfiguration(ORMModel):
    configuration_type: DataOutputTypes
