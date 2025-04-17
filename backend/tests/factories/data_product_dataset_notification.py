import factory
from tests.factories.data_products_datasets import DataProductDatasetAssociationFactory

from app.notifications.enums import NotificationOrigins, NotificationTypes
from app.notifications.model import (
    DataProductDatasetNotification,
)


class DataProductDatasetNotificationFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = DataProductDatasetNotification

    id = factory.Faker("uuid4")
    notification_type = NotificationTypes.DataProductDatasetNotification.value
    notification_origin = NotificationOrigins.APPROVED.value
    data_product_dataset = factory.SubFactory(DataProductDatasetAssociationFactory)
