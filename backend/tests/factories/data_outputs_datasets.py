import factory

from app.authorization.role_assignments.enums import DecisionStatus
from app.data_products.output_port_technical_assets_link.model import (
    DataOutputDatasetAssociation,
)
from tests.factories.technical_asset import TechnicalAssetFactory

from .dataset import DatasetFactory
from .user import UserFactory


class DataOutputDatasetAssociationFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = DataOutputDatasetAssociation

    id = factory.Faker("uuid4")
    status = DecisionStatus.APPROVED
    data_output = factory.SubFactory(TechnicalAssetFactory)
    dataset = factory.SubFactory(DatasetFactory)
    requested_by = factory.SubFactory(UserFactory)
