from typing import ClassVar

from app.technical_asset_configuration.base_schema import TechnicalAssetPlugin


class OtherPlugin(TechnicalAssetPlugin):
    name: ClassVar[str] = "OtherPlugin"
