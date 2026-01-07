import factory

from app.users.notifications.model import Notification
from tests.factories.event import EventFactory
from tests.factories.user import UserFactory


class NotificationFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = Notification

    id = factory.Faker("uuid4")
    user = factory.SubFactory(UserFactory)
    event = factory.SubFactory(EventFactory)
