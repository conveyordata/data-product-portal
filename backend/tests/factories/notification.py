import factory
from tests.factories.data_outputs_datasets import DataOutputDatasetAssociationFactory

from app.notifications.model import (
    Notification,
)
from app.notifications.notification_types import NotificationTypes


class NotificationFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = Notification

    id = factory.Faker("uuid4")
    configuration_type = NotificationTypes.DataOutputDatasetNotification.value
    reference_id = factory.LazyAttribute(
        lambda o: DataOutputDatasetAssociationFactory().id
    )
