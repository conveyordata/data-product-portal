import factory
from faker import Faker

from app.configuration.access_modes.model import AccessMode, DefaultAccessMode

fake = Faker()


class AccessModeFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = AccessMode

    id = factory.Faker("uuid4")
    name = factory.Sequence(lambda _: fake.unique.word())
    description = factory.Faker("text", max_nb_chars=120)
    technical_asset_types = ["FakeLinkPlugin"]


class DefaultAccessModeFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = DefaultAccessMode
        exclude = ("access_mode",)

    access_mode = factory.SubFactory(AccessModeFactory)
    access_mode_id = factory.SelfAttribute("access_mode.id")
    technical_asset_type = factory.LazyAttribute(
        lambda default: default.access_mode.technical_asset_types[0]
    )
