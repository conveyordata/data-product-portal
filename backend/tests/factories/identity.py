import factory
from factory.fuzzy import FuzzyText
from faker import Faker

fake = Faker()


class IdentityFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        abstract = True

    id = factory.Faker("uuid4")
    external_id = FuzzyText(length=10)
