import factory
from tests.factories.data_product_membership import DataProductMembershipFactory

from app.notifications.enums import NotificationOrigins, NotificationTypes
from app.notifications.model import (
    DataProductMembershipNotification,
)


class DataProductMembershipNotificationFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = DataProductMembershipNotification

    id = factory.Faker("uuid4")
    notification_type = NotificationTypes.DataProductMembershipNotification.value
    notification_origin = NotificationOrigins.APPROVED.value
    data_product_membership = factory.SubFactory(DataProductMembershipFactory)
