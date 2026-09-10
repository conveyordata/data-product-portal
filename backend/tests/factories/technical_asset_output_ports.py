import factory

from app.authorization.role_assignments.enums import DecisionStatus
from app.data_products.output_port_technical_assets_link.model import (
    TechnicalAssetOutputPortAssociation,
)
from tests.factories.technical_asset import TechnicalAssetFactory

from .output_port import OutputPortFactory
from .user import UserFactory


class TechnicalAssetOutputPortAssociationFactory(
    factory.alchemy.SQLAlchemyModelFactory
):
    class Meta:
        model = TechnicalAssetOutputPortAssociation

    id = factory.Faker("uuid4")
    status = DecisionStatus.APPROVED
    technical_asset = factory.SubFactory(TechnicalAssetFactory)
    output_port = factory.SubFactory(OutputPortFactory)
    requested_by = factory.SubFactory(UserFactory)
