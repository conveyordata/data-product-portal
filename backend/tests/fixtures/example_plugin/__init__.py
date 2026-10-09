from typing import ClassVar

from app.technical_asset_configuration.base_schema import TechnicalAssetPlugin


class ExamplePlugin(TechnicalAssetPlugin):
    name: ClassVar[str] = "ExamplePlugin"
