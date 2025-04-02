import factory
from tests.factories.data_products_datasets import DataProductDatasetAssociationFactory

from app.notifications.data_product_dataset_association.model import (
    DataProductDatasetNotification,
)
from app.notifications.notification_types import NotificationTypes


class DataProductDatasetNotificationFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = DataProductDatasetNotification

    id = factory.Faker("uuid4")
    configuration_type = NotificationTypes.DataProductDatasetNotification.value
    data_product_dataset = factory.SubFactory(DataProductDatasetAssociationFactory)
