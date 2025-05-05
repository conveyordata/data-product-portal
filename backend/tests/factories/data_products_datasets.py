import factory

from app.data_products_datasets.model import DataProductDatasetAssociation
from app.role_assignments.enums import DecisionStatus

from .data_product import DataProductFactory
from .dataset import DatasetFactory
from .user import UserFactory


class DataProductDatasetAssociationFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = DataProductDatasetAssociation

    id = factory.Faker("uuid4")
    status = DecisionStatus.APPROVED
    data_product = factory.SubFactory(DataProductFactory)
    dataset = factory.SubFactory(DatasetFactory)
    requested_by = factory.SubFactory(UserFactory)
