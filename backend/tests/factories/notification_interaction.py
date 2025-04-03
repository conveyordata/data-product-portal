import factory
from tests.factories.notification import (
    NotificationFactory,
)

from app.notification_interactions.model import NotificationInteraction

from .user import UserFactory


class NotificationInteractionFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = NotificationInteraction

    id = factory.Faker("uuid4")
    user = factory.SubFactory(UserFactory)
    notification = factory.SubFactory(NotificationFactory)
