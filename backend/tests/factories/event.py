import factory
from tests.factories.user import UserFactory

from app.events.enums import EventReferenceEntity, EventType
from app.events.model import Event


class EventFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = Event

    id = factory.Faker("uuid4")
    name = EventType.DATASET_CREATED
    subject_id = factory.Faker("uuid4")
    deleted_subject_identifier = factory.Faker("text", max_nb_chars=20)
    subject_type = EventReferenceEntity.DATASET

    actor = factory.SubFactory(UserFactory)
