from uuid import UUID

from app.shared.schema import ORMModel


class ApproveLinkBetweenTechnicalAssetAndOutputPortRequest(ORMModel):
    output_port_id: UUID


class DenyLinkBetweenTechnicalAssetAndOutputPortRequest(ORMModel):
    output_port_id: UUID
