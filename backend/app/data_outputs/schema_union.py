from typing import Union

from app.data_outputs.data_output_types import DataOutputTypes
from app.data_outputs.databricks_data_output.schema import DatabricksDataOutput
from app.data_outputs.glue_data_output.schema import GlueDataOutput
from app.data_outputs.s3_data_output.schema import S3DataOutput

DataOutputs = Union[S3DataOutput, GlueDataOutput]

DataOutputMap = {
    DataOutputTypes.S3DataOutput: S3DataOutput,
    DataOutputTypes.GlueDataOutput: GlueDataOutput,
    DataOutputTypes.DatabricksDataOutput: DatabricksDataOutput,
}
