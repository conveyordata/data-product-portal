import factory

from app.theme_settings.model import SETTINGS_ID, ThemeSettings


class ThemeSettingsFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = ThemeSettings

    id = SETTINGS_ID
    portal_name = factory.Faker("word")
