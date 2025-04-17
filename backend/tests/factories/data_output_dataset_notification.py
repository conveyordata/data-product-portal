import factory
from tests.factories.data_outputs_datasets import DataOutputDatasetAssociationFactory

from app.notifications.enums import NotificationOrigins, NotificationTypes
from app.notifications.model import (
    DataOutputDatasetNotification,
)


class DataOutputDatasetNotificationFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = DataOutputDatasetNotification

    id = factory.Faker("uuid4")
    notification_type = NotificationTypes.DataOutputDatasetNotification.value
    notification_origin = NotificationOrigins.APPROVED.value
    data_output_dataset = factory.SubFactory(DataOutputDatasetAssociationFactory)
