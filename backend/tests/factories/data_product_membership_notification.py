import factory
from tests.factories.data_product_membership import DataProductMembershipFactory

from app.notifications.data_product_membership.model import (
    DataProductMembershipNotification,
)
from app.notifications.notification_types import NotificationTypes


class DataProductMembershipNotificationFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = DataProductMembershipNotification

    id = factory.Faker("uuid4")
    configuration_type = NotificationTypes.DataProductMembership.value
    data_product_membership = factory.SubFactory(DataProductMembershipFactory)
