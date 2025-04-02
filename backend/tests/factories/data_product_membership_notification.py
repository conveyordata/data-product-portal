import factory
from tests.factories.data_product_membership import DataProductMembershipFactory

from app.notifications.model import (
    Notification,
)
from app.notifications.notification_types import NotificationTypes


class DataProductMembershipNotificationFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = Notification

    id = factory.Faker("uuid4")
    configuration_type = NotificationTypes.DataProductMembershipNotification.value
    reference_id = factory.LazyAttribute(lambda o: DataProductMembershipFactory().id)
