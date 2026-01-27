import factory

from app.data_products.technical_assets.model import DataOutput
from app.data_products.technical_assets.status import TechnicalAssetStatus
from tests import test_session
from tests.factories.data_product import DataProductFactory
from tests.factories.platform_service import PlatformServiceFactory
from tests.factories.s3_data_output import S3DataOutputFactory
from tests.factories.tags import TagFactory


class DataOutputFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = DataOutput

    id = factory.Faker("uuid4")
    name = factory.Faker("word")
    namespace = factory.Faker("word")
    description = factory.Faker("text", max_nb_chars=20)
    status = TechnicalAssetStatus.ACTIVE.value

    service = factory.SubFactory(PlatformServiceFactory)

    @factory.post_generation
    def platform_id(self, create, extracted, **kwargs):
        self.platform_id = self.service.platform_id
        test_session.commit()

    owner = factory.SubFactory(DataProductFactory)

    technical_mapping = "default"
    configuration = factory.SubFactory(S3DataOutputFactory)

    @factory.post_generation
    def tags(self, create, extracted, **kwargs):
        if not create:
            # If we are just doing DataOutputFactory.build(), don't save tags
            return

        if extracted:
            # If called as: DataOutputFactory(tags=[tag1, tag2])
            for tag in extracted:
                self.tags.append(tag)
        else:
            # If called without arguments, create a default tag
            self.tags.append(TagFactory())
        test_session.commit()
