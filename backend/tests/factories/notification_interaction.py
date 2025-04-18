import factory

from app.notification_interactions.model import NotificationInteraction
from app.notifications.model import DataProductDatasetNotification

from .user import UserFactory


class NotificationInteractionFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = NotificationInteraction

    id = factory.Faker("uuid4")
    user = factory.SubFactory(UserFactory)
    notification = factory.SubFactory(DataProductDatasetNotification)
