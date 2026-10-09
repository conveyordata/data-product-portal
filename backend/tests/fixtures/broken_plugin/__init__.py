from typing import ClassVar

from app.technical_asset_configuration.base_schema import TechnicalAssetPlugin


class BrokenPlugin(TechnicalAssetPlugin):
    name: ClassVar[str] = "BrokenPlugin"
