from typing import Optional
from uuid import UUID

from app.data_products.technical_assets.enums import TechnicalMapping
from app.data_products.technical_assets.status import TechnicalAssetStatus
from app.shared.schema import ORMModel
from app.technical_asset_configuration.schema_union import DataOutputConfiguration


class TechnicalAsset(ORMModel):
    id: UUID
    name: str
    namespace: str
    description: str
    status: TechnicalAssetStatus
    technical_mapping: TechnicalMapping
    owner_id: UUID
    # Exactly one of `configuration` (a built-in type) or `plugin_key` (a
    # dynamically loaded plugin, ADR-0024) is set - see
    # app/data_products/technical_assets/schema_response.py for the same shape.
    platform_id: Optional[UUID] = None
    service_id: Optional[UUID] = None
    configuration: Optional[DataOutputConfiguration] = None
    plugin_key: Optional[str] = None
