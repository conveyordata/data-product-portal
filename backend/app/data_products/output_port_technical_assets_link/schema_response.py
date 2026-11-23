from datetime import datetime
from typing import Optional
from uuid import UUID

from app.authorization.role_assignments.enums import DecisionStatus
from app.data_products.output_ports.schema import OutputPort
from app.data_products.technical_assets.schema import (
    TechnicalAsset as TechnicalAssetBaseSchema,
)
from app.shared.schema import ORMModel
from app.users.schema import User


class TechnicalAssetOutputPortAssociationsGet(ORMModel):
    id: UUID
    output_port_id: UUID
    output_port: OutputPort
    technical_asset_id: UUID
    technical_asset: TechnicalAssetBaseSchema
    status: DecisionStatus
    requested_on: datetime
    denied_on: Optional[datetime]
    approved_on: Optional[datetime]

    requested_by: Optional[User]
    deleted_requested_by_identifier: Optional[str] = None
    denied_by: Optional[User]
    deleted_denied_by_identifier: Optional[str] = None
    approved_by: Optional[User]
    deleted_approved_by_identifier: Optional[str] = None


class LinkTechnicalAssetsToOutputPortResponse(ORMModel):
    link_id: UUID
