from typing import Annotated, Union

from pydantic import Field

from app.data_output_configuration.data_output_types import DataOutputTypes
from app.data_output_configuration.databricks.schema import (
    DatabricksTechnicalAssetConfiguration,
)
from app.data_output_configuration.glue.schema import GlueTechnicalAssetConfiguration
from app.data_output_configuration.postgresql.schema import (
    PostgresTechnicalAssetConfiguration,
)
from app.data_output_configuration.redshift.schema import (
    RedshiftTechnicalAssetConfiguration,
)
from app.data_output_configuration.s3.schema import S3TechnicalAssetConfiguration
from app.data_output_configuration.snowflake.schema import (
    SnowflakeTechnicalAssetConfiguration,
)

DataOutputs = Union[
    S3TechnicalAssetConfiguration,
    GlueTechnicalAssetConfiguration,
    DatabricksTechnicalAssetConfiguration,
    SnowflakeTechnicalAssetConfiguration,
    RedshiftTechnicalAssetConfiguration,
    PostgresTechnicalAssetConfiguration,
]

DataOutputMap = {
    DataOutputTypes.S3TechnicalAssetConfiguration: S3TechnicalAssetConfiguration,
    DataOutputTypes.GlueTechnicalAssetConfiguration: GlueTechnicalAssetConfiguration,
    DataOutputTypes.DatabricksTechnicalAssetConfiguration: DatabricksTechnicalAssetConfiguration,
    DataOutputTypes.SnowflakeTechnicalAssetConfiguration: SnowflakeTechnicalAssetConfiguration,
    DataOutputTypes.RedshiftTechnicalAssetConfiguration: RedshiftTechnicalAssetConfiguration,
    DataOutputTypes.PostgresTechnicalAssetConfiguration: PostgresTechnicalAssetConfiguration,
}

DataOutputConfiguration = Annotated[
    DataOutputs,
    Field(discriminator="configuration_type"),
]
