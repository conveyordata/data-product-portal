from typing import Annotated, Any

from fastapi import HTTPException, status
from pydantic import PlainSerializer, PlainValidator, WithJsonSchema

from app.plugins.registry import plugin_registry
from app.technical_asset_configuration.base_schema import TechnicalAssetPlugin

plugin_registry.discovered()


def technical_asset_validator(value: Any) -> TechnicalAssetPlugin:
    if isinstance(value, TechnicalAssetPlugin):
        return value

    if isinstance(value, dict):
        name = value.get("name")
    else:
        name = getattr(value, "name", None) or getattr(
            value, "configuration_type", None
        )
    if not name:
        raise ValueError("name is required")

    plugin = plugin_registry.get(name)
    if not hasattr(plugin, "Meta"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Plugin '{name}' has no configuration of its own",
        )
    return plugin.model_validate(value)


DataOutputConfiguration = Annotated[
    TechnicalAssetPlugin,
    PlainValidator(technical_asset_validator),
    PlainSerializer(lambda configuration: configuration.model_dump(), return_type=dict),
    WithJsonSchema(
        {
            "type": "object",
            "required": ["name"],
            "properties": {"name": {"type": "string"}},
            "additionalProperties": True,
            "description": (
                "Configuration of the technical asset. The available fields depend on "
                "`name`; retrieve them from /v2/plugins/{name}/form."
            ),
        }
    ),
]
