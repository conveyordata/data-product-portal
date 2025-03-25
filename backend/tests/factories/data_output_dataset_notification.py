import factory
from tests.factories.data_outputs_datasets import DataOutputDatasetAssociationFactory

from app.notifications.data_output_dataset_association.model import (
    DataOutputDatasetNotification,
)
from app.notifications.notification_types import NotificationTypes


class DataOutputDatasetNotificationFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = DataOutputDatasetNotification

    id = factory.Faker("uuid4")
    configuration_type = NotificationTypes.DataOutputDataset.value
    data_output_dataset = factory.SubFactory(DataOutputDatasetAssociationFactory)
