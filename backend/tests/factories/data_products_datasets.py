import factory

from app.data_products_datasets.enums import DataProductDatasetLinkStatus
from app.data_products_datasets.model import DataProductDatasetAssociation

from .data_product import DataProductFactory
from .dataset import DatasetFactory


class DataProductDatasetAssociationFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = DataProductDatasetAssociation

    id = factory.Faker("uuid4")
    status = DataProductDatasetLinkStatus.APPROVED.value
    data_product = factory.SubFactory(DataProductFactory)
    dataset = factory.SubFactory(DatasetFactory)
