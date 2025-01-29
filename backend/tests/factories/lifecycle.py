import factory

from app.data_product_lifecycles.model import DataProductLifecycle


class LifecycleFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = DataProductLifecycle

    id = factory.Faker("uuid4")
    name = factory.Faker("word")
    value = factory.Faker("pyint")
    color = factory.Faker("word")
