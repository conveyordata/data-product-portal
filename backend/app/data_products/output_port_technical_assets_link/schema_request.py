from uuid import UUID

from app.shared.schema import ORMModel


class ApproveLinkBetweenTechnicalAssetAndOutputPortRequest(ORMModel):
    technical_asset_id: UUID


class DenyLinkBetweenTechnicalAssetAndOutputPortRequest(ORMModel):
    technical_asset_id: UUID


class LinkTechnicalAssetToOutputPortRequest(ORMModel):
    technical_asset_id: UUID


class UnLinkTechnicalAssetToOutputPortRequest(ORMModel):
    technical_asset_id: UUID
