import factory
from tests.factories.data_products_datasets import DataProductDatasetAssociationFactory
from tests.factories.user import UserFactory

from app.notifications.enums import NotificationTypes
from app.notifications.model import (
    DataProductDatasetNotification,
)
from app.role_assignments.enums import DecisionStatus


class DataProductDatasetNotificationFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = DataProductDatasetNotification

    id = factory.Faker("uuid4")
    notification_type = NotificationTypes.DataProductDatasetNotification.value
    notification_origin = DecisionStatus.APPROVED
    data_product_dataset_id = factory.LazyFunction(
        lambda: DataProductDatasetAssociationFactory().id
    )
    user = factory.SubFactory(UserFactory)
