from datetime import date
from decimal import Decimal

import factory

from app.data_products.output_ports.cost.model import OutputPortCostRecord

from .dataset import DatasetFactory


class OutputPortCostRecordFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = OutputPortCostRecord

    id = factory.Faker("uuid4")
    output_port_id = factory.LazyAttribute(lambda o: DatasetFactory().id)
    recorded_at = factory.LazyFunction(date.today)
    compute_cost = Decimal("50.00")
    storage_cost = Decimal("30.00")
    platform_overhead_cost = Decimal("20.00")
