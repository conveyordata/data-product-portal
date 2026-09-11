"""Discovery-only endpoints for dynamically loaded plugins.

Creating and reading a plugin-backed technical asset goes through the real
`/v2/data_products/{data_product_id}/technical_assets` endpoints now (see
`app/data_products/technical_assets/router.py`/`service.py`) - not a
separate, plugin-specific API. See docs/adr/0024-dynamic-plugin-system.md,
"How the API describes a plugin's configuration".

What's left here is genuinely generic, low-level discovery: which plugins
are installed, and their icon. Whether/how a plugin's `fields` get bridged
into the richer `UIElementMetadata` the frontend's technical-asset form
already renders is a separate, not-yet-settled design question - not
implemented here.
"""

from fastapi import APIRouter, HTTPException, Response

from app.plugins.loader import discover_plugins
from app.plugins.schema import PluginListResponse, PluginSummary

router = APIRouter(prefix="/v2/plugins/dynamic", tags=["Dynamic Plugins"])


@router.get("/")
def list_plugins() -> PluginListResponse:
    return PluginListResponse(
        plugins=[
            PluginSummary(
                key=plugin_cls.key,
                display_name=plugin_cls.display_name,
                fields=plugin_cls.fields,
            )
            for plugin_cls in discover_plugins()
        ]
    )


@router.get("/{key}/icon")
def get_plugin_icon(key: str) -> Response:
    for plugin_cls in discover_plugins():
        if plugin_cls.key == key:
            return Response(content=plugin_cls.get_icon(), media_type="image/svg+xml")
    raise HTTPException(status_code=404, detail=f"No plugin registered for key '{key}'")
