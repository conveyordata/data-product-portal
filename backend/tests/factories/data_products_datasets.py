import factory

from app.authorization.role_assignments.enums import DecisionStatus
from app.data_products_datasets.model import DataProductDatasetAssociation

from .data_product import DataProductFactory
from .dataset import DatasetFactory
from .user import UserFactory


class DataProductDatasetAssociationFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = DataProductDatasetAssociation

    id = factory.Faker("uuid4")
    justification = factory.Faker("text", max_nb_chars=20)
    status = DecisionStatus.APPROVED
    data_product = factory.SubFactory(DataProductFactory)
    dataset = factory.SubFactory(DatasetFactory)
    requested_by = factory.SubFactory(UserFactory)
