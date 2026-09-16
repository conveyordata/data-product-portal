"""The technical asset configuration union, and the import site that registers
every plugin class.

Importing a plugin's module is what makes it a subclass the registry can see, so
the plugins with no configuration of their own (Agno, Coder, Conveyor, GitHub)
are imported here too, for that side effect only.
"""

from typing import Annotated, Union

from pydantic import Field

from app.technical_asset_configuration.agno.schema import AgnoPlugin  # noqa: F401
from app.technical_asset_configuration.azure_blob.schema import (
    AzureBlobTechnicalAssetConfiguration,
)
from app.technical_asset_configuration.coder.schema import CoderPlugin  # noqa: F401
from app.technical_asset_configuration.conveyor.schema import (  # noqa: F401
    ConveyorPlugin,
)
from app.technical_asset_configuration.data_output_types import DataOutputTypes
from app.technical_asset_configuration.databricks.schema import (
    DatabricksTechnicalAssetConfiguration,
)
from app.technical_asset_configuration.github.schema import (  # noqa: F401
    GitHubPlugin,
)
from app.technical_asset_configuration.glue.schema import (
    GlueTechnicalAssetConfiguration,
)
from app.technical_asset_configuration.osi_sem_model.schema import (
    OSISemanticModelTechnicalAssetConfiguration,
)
from app.technical_asset_configuration.postgresql.schema import (
    PostgreSQLTechnicalAssetConfiguration,
)
from app.technical_asset_configuration.redshift.schema import (
    RedshiftTechnicalAssetConfiguration,
)
from app.technical_asset_configuration.rustfs.schema import (
    RustFSTechnicalAssetConfiguration,
)
from app.technical_asset_configuration.s3.schema import S3TechnicalAssetConfiguration
from app.technical_asset_configuration.snowflake.schema import (
    SnowflakeTechnicalAssetConfiguration,
)

DataOutputs = Union[
    S3TechnicalAssetConfiguration,
    RustFSTechnicalAssetConfiguration,
    GlueTechnicalAssetConfiguration,
    DatabricksTechnicalAssetConfiguration,
    SnowflakeTechnicalAssetConfiguration,
    RedshiftTechnicalAssetConfiguration,
    PostgreSQLTechnicalAssetConfiguration,
    OSISemanticModelTechnicalAssetConfiguration,
    AzureBlobTechnicalAssetConfiguration,
]

DataOutputMap = {
    DataOutputTypes.S3TechnicalAssetConfiguration: S3TechnicalAssetConfiguration,
    DataOutputTypes.RustFSTechnicalAssetConfiguration: RustFSTechnicalAssetConfiguration,
    DataOutputTypes.GlueTechnicalAssetConfiguration: GlueTechnicalAssetConfiguration,
    DataOutputTypes.DatabricksTechnicalAssetConfiguration: DatabricksTechnicalAssetConfiguration,
    DataOutputTypes.SnowflakeTechnicalAssetConfiguration: SnowflakeTechnicalAssetConfiguration,
    DataOutputTypes.RedshiftTechnicalAssetConfiguration: RedshiftTechnicalAssetConfiguration,
    DataOutputTypes.PostgreSQLTechnicalAssetConfiguration: PostgreSQLTechnicalAssetConfiguration,
    DataOutputTypes.OSISemanticModelTechnicalAssetConfiguration: OSISemanticModelTechnicalAssetConfiguration,
    DataOutputTypes.AzureBlobTechnicalAssetConfiguration: AzureBlobTechnicalAssetConfiguration,
}

DataOutputConfiguration = Annotated[
    DataOutputs,
    Field(discriminator="configuration_type"),
]
