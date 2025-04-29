from typing import Annotated, Union

from pydantic import Field

from app.data_output_configuration.data_output_types import DataOutputTypes
from app.data_output_configuration.databricks.schema import DatabricksDataOutput
from app.data_output_configuration.glue.schema import GlueDataOutput
from app.data_output_configuration.redshift.schema import RedshiftDataOutput
from app.data_output_configuration.s3.schema import S3DataOutput
from app.data_output_configuration.snowflake.schema import SnowflakeDataOutput

DataOutputs = Union[
    S3DataOutput,
    GlueDataOutput,
    DatabricksDataOutput,
    SnowflakeDataOutput,
    RedshiftDataOutput,
]

DataOutputMap = {
    DataOutputTypes.S3DataOutput: S3DataOutput,
    DataOutputTypes.GlueDataOutput: GlueDataOutput,
    DataOutputTypes.DatabricksDataOutput: DatabricksDataOutput,
    DataOutputTypes.SnowflakeDataOutput: SnowflakeDataOutput,
    DataOutputTypes.RedshiftDataOutput: RedshiftDataOutput,
}

DataOutputConfiguration = Annotated[
    DataOutputs,
    Field(discriminator="configuration_type"),
]
