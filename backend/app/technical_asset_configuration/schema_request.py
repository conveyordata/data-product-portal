from typing import Any, Optional
from uuid import UUID

from pydantic import model_validator

from app.shared.schema import ORMModel
from app.technical_asset_configuration.schema_union import DataOutputConfiguration


class RenderTechnicalAssetAccessPathRequest(ORMModel):
    platform_id: Optional[UUID] = None
    service_id: Optional[UUID] = None
    configuration: Optional[DataOutputConfiguration] = None
    plugin_key: Optional[str] = None
    values: Optional[dict[str, Any]] = None

    @model_validator(mode="after")
    def validate_configuration_shape(self):
        if (self.plugin_key is not None) == (self.configuration is not None):
            raise ValueError(
                "Provide exactly one of `configuration` (a built-in type) or "
                "`plugin_key` (a dynamically loaded plugin)."
            )
        return self
