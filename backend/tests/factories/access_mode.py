import factory
from faker import Faker

from app.configuration.access_modes.model import AccessMode

fake = Faker()


class AccessModeFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = AccessMode

    id = factory.Faker("uuid4")
    name = factory.Sequence(lambda _: fake.unique.word())
    description = factory.Faker("text", max_nb_chars=120)
