from enum import Enum


class DataOutputTypes(str, Enum):
    S3DataOutput = "S3DataOutput"
    DatabricksDataOutput = "DatabricksDataOutput"
    GlueDataOutput = "GlueDataOutput"
    SnowflakeDataOutput = "SnowflakeDataOutput"
