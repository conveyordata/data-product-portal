import factory
from factory.fuzzy import FuzzyText
from faker import Faker

from .model_factory import ModelFactory

fake = Faker()


class IdentityFactory[T](ModelFactory[T]):
    class Meta:
        abstract = True

    id = factory.Faker("uuid4")
    external_id = FuzzyText(length=10)
