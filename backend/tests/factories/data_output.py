import factory
from tests import test_session
from tests.factories.data_product import DataProductFactory
from tests.factories.platform_service import PlatformServiceFactory
from tests.factories.s3_data_output import S3DataOutputFactory

from app.data_outputs.model import DataOutput
from app.data_outputs.status import DataOutputStatus


class DataOutputFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = DataOutput

    id = factory.Faker("uuid4")
    name = factory.Faker("word")
    namespace = "namespace"
    description = factory.Faker("text", max_nb_chars=20)
    status = DataOutputStatus.ACTIVE.value

    service = factory.SubFactory(PlatformServiceFactory)

    @factory.post_generation
    def platform_id(self, create, extracted, **kwargs):
        self.platform_id = self.service.platform_id
        test_session.commit()

    owner = factory.SubFactory(DataProductFactory)

    sourceAligned = False
    configuration = factory.SubFactory(S3DataOutputFactory)
