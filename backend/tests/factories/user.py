import factory
from factory.fuzzy import FuzzyText

from app.users.model import User


class UserFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = User

    id = factory.Faker("uuid4")
    email = factory.Faker("email")
    external_id = FuzzyText(length=10)
    first_name = factory.Faker("first_name")
    last_name = factory.Faker("last_name")
    is_admin = False
    is_deleted = False
