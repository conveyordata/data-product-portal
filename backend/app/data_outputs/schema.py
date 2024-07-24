from uuid import UUID

from app.data_outputs.schema_union import DataOutputs, DataOutputTypes
from app.data_products.schema import DataProduct
from app.shared.schema import ORMModel


class DataOutputCreate(ORMModel):
    name: str
    external_id: str
    owner_id: UUID
    configuration: DataOutputs


class DataOutputRegister(ORMModel):
    name: str
    external_id: str
    configuration: DataOutputs


class DataOutput(ORMModel):
    id: UUID
    name: str
    external_id: str
    owner: DataProduct
    configuration: DataOutputs
    configuration_type: DataOutputTypes


class DataOutputToDB(ORMModel):
    name: str
    external_id: str
    owner_id: UUID
    configuration: str
    configuration_type: DataOutputTypes
