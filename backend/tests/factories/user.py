import factory
from factory.fuzzy import FuzzyText
from faker import Faker

from app.users.model import User

fake = Faker()


class UserFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = User

    id = factory.Faker("uuid4")
    email = factory.Sequence(lambda _: fake.unique.email())
    external_id = FuzzyText(length=10)
    first_name = factory.Faker("first_name")
    last_name = factory.Faker("last_name")
