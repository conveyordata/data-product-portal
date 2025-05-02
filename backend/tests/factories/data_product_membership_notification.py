import factory
from tests.factories.data_product_membership import DataProductMembershipFactory
from tests.factories.user import UserFactory

from app.notifications.enums import NotificationTypes
from app.notifications.model import (
    DataProductMembershipNotification,
)
from app.role_assignments.enums import DecisionStatus


class DataProductMembershipNotificationFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = DataProductMembershipNotification

    id = factory.Faker("uuid4")
    notification_type = NotificationTypes.DataProductMembershipNotification.value
    notification_origin = DecisionStatus.APPROVED
    data_product_membership_id = factory.LazyFunction(
        lambda: DataProductMembershipFactory().id
    )
    user = factory.SubFactory(UserFactory)
