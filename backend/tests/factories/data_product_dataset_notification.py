import factory
from tests.factories.data_products_datasets import DataProductDatasetAssociationFactory

from app.data_products_datasets.enums import DataProductDatasetLinkStatus
from app.notifications.model import (
    DataProductDatasetNotification,
)
from app.notifications.notification_types import NotificationTypes


class DataProductDatasetNotificationFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = DataProductDatasetNotification

    id = factory.Faker("uuid4")
    notification_type = NotificationTypes.DataProductDatasetNotification.value
    notification_origin = DataProductDatasetLinkStatus.APPROVED
    data_product_dataset = factory.SubFactory(DataProductDatasetAssociationFactory)
