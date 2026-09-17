from typing import Annotated, Any

from fastapi import HTTPException, status
from pydantic import PlainSerializer, PlainValidator, WithJsonSchema

from app.plugins.registry import plugin_registry
from app.technical_asset_configuration.base_schema import TechnicalAssetPlugin

plugin_registry.discovered()


def _resolve_configuration(value: Any) -> TechnicalAssetPlugin:
    if isinstance(value, TechnicalAssetPlugin):
        return value

    configuration_type = (
        value.get("configuration_type")
        if isinstance(value, dict)
        else getattr(value, "configuration_type", None)
    )
    if not configuration_type:
        raise ValueError("configuration_type is required")

    plugin = plugin_registry.get(configuration_type)
    if not hasattr(plugin, "Meta"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Plugin '{configuration_type}' has no configuration of its own",
        )
    return plugin.model_validate(value)


DataOutputConfiguration = Annotated[
    TechnicalAssetPlugin,
    PlainValidator(_resolve_configuration),
    PlainSerializer(lambda configuration: configuration.model_dump(), return_type=dict),
    WithJsonSchema(
        {
            "type": "object",
            "required": ["configuration_type"],
            "properties": {"configuration_type": {"type": "string"}},
            "additionalProperties": True,
            "description": (
                "Configuration of the technical asset. The available fields depend on "
                "`configuration_type`; retrieve them from /v2/plugins/{name}/form."
            ),
        }
    ),
]
