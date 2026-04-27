from datetime import UTC, datetime

import factory

from app.data_products.output_ports.freshness.model import FreshnessObservation

from .dataset import DatasetFactory


class FreshnessObservationFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = FreshnessObservation

    id = factory.Faker("uuid4")
    output_port_id = factory.LazyAttribute(lambda o: DatasetFactory().id)
    last_refreshed_at = factory.LazyFunction(lambda: datetime.now(UTC))
