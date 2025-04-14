import factory
from tests.factories.data_product_membership import DataProductMembershipFactory

from app.data_product_memberships.enums import DataProductMembershipStatus
from app.notifications.model import (
    DataProductMembershipNotification,
)
from app.notifications.notification_types import NotificationTypes


class DataProductMembershipNotificationFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = DataProductMembershipNotification

    id = factory.Faker("uuid4")
    notification_type = NotificationTypes.DataProductMembershipNotification.value
    notification_origin = DataProductMembershipStatus.APPROVED
    data_product_membership = factory.SubFactory(DataProductMembershipFactory)
