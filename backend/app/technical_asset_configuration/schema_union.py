from typing import Annotated, Any

from pydantic import PlainSerializer, PlainValidator, WithJsonSchema

from app.technical_asset_configuration.agno.schema import AgnoPlugin  # noqa: F401
from app.technical_asset_configuration.azure_blob.schema import (  # noqa: F401
    AzureBlobTechnicalAssetConfiguration,
)
from app.technical_asset_configuration.base_schema import TechnicalAssetPlugin
from app.technical_asset_configuration.coder.schema import CoderPlugin  # noqa: F401
from app.technical_asset_configuration.conveyor.schema import (  # noqa: F401
    ConveyorPlugin,
)
from app.technical_asset_configuration.databricks.schema import (  # noqa: F401
    DatabricksTechnicalAssetConfiguration,
)
from app.technical_asset_configuration.github.schema import (  # noqa: F401
    GitHubPlugin,
)
from app.technical_asset_configuration.glue.schema import (  # noqa: F401
    GlueTechnicalAssetConfiguration,
)
from app.technical_asset_configuration.osi_sem_model.schema import (  # noqa: F401
    OSISemanticModelTechnicalAssetConfiguration,
)
from app.technical_asset_configuration.postgresql.schema import (  # noqa: F401
    PostgreSQLTechnicalAssetConfiguration,
)
from app.technical_asset_configuration.redshift.schema import (  # noqa: F401
    RedshiftTechnicalAssetConfiguration,
)
from app.technical_asset_configuration.rustfs.schema import (  # noqa: F401
    RustFSTechnicalAssetConfiguration,
)
from app.technical_asset_configuration.s3.schema import (  # noqa: F401
    S3TechnicalAssetConfiguration,
)
from app.technical_asset_configuration.snowflake.schema import (  # noqa: F401
    SnowflakeTechnicalAssetConfiguration,
)


def _resolve_configuration(value: Any) -> TechnicalAssetPlugin:
    from app.plugins.registry import plugin_registry

    if isinstance(value, TechnicalAssetPlugin):
        return value

    configuration_type = (
        value.get("configuration_type")
        if isinstance(value, dict)
        else getattr(value, "configuration_type", None)
    )
    if not configuration_type:
        raise ValueError("configuration_type is required")

    return plugin_registry.get(configuration_type).model_validate(value)


DataOutputConfiguration = Annotated[
    TechnicalAssetPlugin,
    PlainValidator(_resolve_configuration),
    PlainSerializer(lambda configuration: configuration.model_dump(), return_type=dict),
    WithJsonSchema(
        {
            "type": "object",
            "additionalProperties": True,
            "description": (
                "Configuration of the technical asset. The available fields depend on "
                "`configuration_type`; retrieve them from /v2/plugins/{name}/form."
            ),
        }
    ),
]
