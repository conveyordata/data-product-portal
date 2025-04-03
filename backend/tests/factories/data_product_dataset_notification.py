import factory
from tests.factories.data_products_datasets import DataProductDatasetAssociationFactory

from app.notifications.model import (
    Notification,
)
from app.notifications.notification_types import NotificationTypes


class DataProductDatasetNotificationFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = Notification

    id = factory.Faker("uuid4")
    configuration_type = NotificationTypes.DataProductDatasetNotification.value
    reference_id = factory.LazyAttribute(
        lambda o: DataProductDatasetAssociationFactory().id
    )
