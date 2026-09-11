"""Azure Blob Storage technical asset plugin.

Inherits from the SDK's `TechnicalAssetPlugin` (ADR-0024) - a plugin depends
on the SDK, not the portal itself. The portal loads plugin classes by entry
point, never by importing the portal into the plugin's own process.
"""

import logging
import re
from typing import Any, ClassVar

from example_azure_blob.models import AzureBlobAsset
from sdk.plugins.base import PluginField, TechnicalAssetPlugin

logger = logging.getLogger(__name__)

# Azure's own container naming rules: 3-63 chars, lowercase letters, digits
# and hyphens, must start and end with a letter or digit.
CONTAINER_NAME_PATTERN = r"^[a-z0-9](?:[a-z0-9-]{1,61}[a-z0-9])?$"


class PluginValidationError(Exception):
    pass


class AzureBlobPlugin(TechnicalAssetPlugin):
    key: ClassVar[str] = "azure-blob"
    display_name: ClassVar[str] = "Azure Blob Storage"

    # Read via importlib.resources at call time - never inlined as a string.
    icon_package: ClassVar[str] = "example_azure_blob"
    icon_resource: ClassVar[str] = "icon.svg"

    fields: ClassVar[list[PluginField]] = [
        {
            "name": "container_name",
            "label": "Container name",
            "type": "string",
            "required": True,
            "pattern": CONTAINER_NAME_PATTERN,
            "tooltip": "3-63 lowercase letters, numbers or hyphens.",
        },
        {"name": "path", "label": "Path", "type": "string", "required": False},
        {
            "name": "access_tier",
            "label": "Access tier",
            "type": "string",
            "required": False,
        },
    ]

    # The plugin hardcodes the revision it wants; the portal reconciles its
    # table to this on every `db_tool migrate`.
    target_revision: ClassVar[str] = "azureblob_0003_drop_technical_asset_id"
    migrations_package: ClassVar[str] = "example_azure_blob"

    model: ClassVar[type] = AzureBlobAsset

    # Opts into the portal's existing environment model (ADR-0024) - the
    # access-tile UI shows an environment picker, and `get_url`'s context
    # carries the resolved `Environment.context` for whichever environment
    # was picked (see `azure_development`/`azure_production` in
    # sample_data.sql).
    has_environments: ClassVar[bool] = True

    @classmethod
    def validate(cls, values: dict[str, Any], context: Any) -> None:
        logger.info(f"validate() values={values!r} context={context!r}")
        container_name = values.get("container_name")
        if not container_name or not isinstance(container_name, str):
            raise PluginValidationError("container_name is required")
        if not re.match(CONTAINER_NAME_PATTERN, container_name):
            raise PluginValidationError(
                "container_name must be 3-63 lowercase letters, numbers or hyphens"
            )

    @classmethod
    def render_result(cls, values: dict[str, Any], context: Any) -> str:
        logger.info(f"render_result() values={values!r} context={context!r}")
        container_name = values["container_name"]
        path = values.get("path") or ""
        domain = getattr(context, "domain", None) or "example"
        return f"https://{domain}.blob.core.windows.net/{container_name}/{path}".rstrip(
            "/"
        )

    @classmethod
    def get_url(cls, values: dict[str, Any], context: Any) -> str:
        logger.info(f"get_url() values={values!r} context={context!r}")
        environment_context = getattr(context, "environment_context", None)
        if environment_context:
            # `environment_context` is the environment's own `Environment.context`
            # value, already namespace-substituted by the portal - here it's a
            # storage-account URL template, e.g.
            # "https://{{}}.blob.core.windows.net/" -> the data product's
            # own storage account for that environment.
            return environment_context
        return "https://portal.azure.com/"
