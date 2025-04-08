import factory
from tests import test_session

from app.datasets.enums import DatasetAccessType
from app.datasets.model import Dataset
from app.datasets.status import DatasetStatus

from .domain import DomainFactory
from .user import UserFactory


class DatasetFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = Dataset

    id = factory.Faker("uuid4")
    namespace = "namespace"
    name = factory.Faker("word")
    description = factory.Faker("text", max_nb_chars=20)
    about = factory.Faker("text", max_nb_chars=20)
    status = DatasetStatus.ACTIVE.value
    access_type = DatasetAccessType.PUBLIC.value
    domain = factory.SubFactory(DomainFactory)

    @factory.post_generation
    def owners(self, create, extracted, **kwargs):
        if not create:
            return

        if not extracted:
            extracted = [UserFactory()]

        for user in extracted:
            self.owners.append(user)
            test_session.commit()
