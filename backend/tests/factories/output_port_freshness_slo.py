from datetime import time

import factory

from app.data_products.output_ports.freshness.model import FreshnessSlo

from .dataset import DatasetFactory


class FreshnessSloFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = FreshnessSlo

    id = factory.Faker("uuid4")
    output_port_id = factory.LazyAttribute(lambda o: DatasetFactory().id)
    deadline_time = time(8, 0, 0)
