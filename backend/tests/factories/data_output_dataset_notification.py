import factory
from tests.factories.data_outputs_datasets import DataOutputDatasetAssociationFactory
from tests.factories.user import UserFactory

from app.notifications.enums import NotificationTypes
from app.notifications.model import (
    DataOutputDatasetNotification,
)
from app.role_assignments.enums import DecisionStatus


class DataOutputDatasetNotificationFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = DataOutputDatasetNotification

    id = factory.Faker("uuid4")
    notification_type = NotificationTypes.DataOutputDatasetNotification.value
    notification_origin = DecisionStatus.APPROVED

    data_output_dataset = factory.SubFactory(DataOutputDatasetAssociationFactory)

    data_output_dataset_id = factory.LazyAttribute(
        lambda obj: obj.data_output_dataset.id
    )
    data_output_id = factory.LazyAttribute(
        lambda obj: obj.data_output_dataset.data_output_id
    )
    data_product_id = factory.LazyAttribute(
        lambda obj: obj.data_output_dataset.data_output.owner_id
    )
    dataset_id = factory.LazyAttribute(lambda obj: obj.data_output_dataset.dataset_id)

    user = factory.SubFactory(UserFactory)
