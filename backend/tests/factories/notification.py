import factory
from tests.factories.event import EventFactory
from tests.factories.user import UserFactory

from app.notifications.model import Notification


class NotificationFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = Notification

    id = factory.Faker("uuid4")
    user = factory.SubFactory(UserFactory)
    event = factory.SubFactory(EventFactory)
