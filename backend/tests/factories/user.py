import factory
from faker import Faker

from app.users.model import User
from tests.factories.identity import IdentityFactory

fake = Faker()


class UserFactory(IdentityFactory):
    class Meta:
        model = User

    email = factory.Sequence(lambda _: fake.unique.email())
    first_name = factory.Faker("first_name")
    last_name = factory.Faker("last_name")
