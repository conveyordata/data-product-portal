import factory

from app.datasets.enums import DatasetAccessType
from app.datasets.model import Dataset
from app.datasets.status import DatasetStatus

from .domain import DomainFactory


class DatasetFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = Dataset

    id = factory.Faker("uuid4")
    namespace = factory.Faker("word")
    name = factory.Faker("word")
    description = factory.Faker("text", max_nb_chars=20)
    about = factory.Faker("text", max_nb_chars=20)
    status = DatasetStatus.ACTIVE.value
    access_type = DatasetAccessType.PUBLIC.value
    domain = factory.SubFactory(DomainFactory)
    usage = factory.Faker("word")
