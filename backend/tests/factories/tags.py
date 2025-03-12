import factory

from app.tags.model import Tag


class TagFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = Tag

    id = factory.Faker("uuid4")
    value = factory.Faker("word")
