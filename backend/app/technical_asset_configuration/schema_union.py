from typing import Annotated, Any

from pydantic import PlainSerializer, PlainValidator, WithJsonSchema

from app.technical_asset_configuration.base_schema import TechnicalAssetPlugin


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
