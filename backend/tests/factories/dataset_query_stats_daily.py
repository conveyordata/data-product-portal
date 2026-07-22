import factory

from app.data_products.output_ports.query_stats.model import (
    DatasetQueryStatsDaily,
)

from .data_product import DataProductFactory
from .dataset import OutputPortFactory


class OutputPortQueryStatsFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = DatasetQueryStatsDaily

    date = factory.Faker("date_object")
    output_port_id = factory.LazyAttribute(
        lambda o: (
            OutputPortFactory().id
            if not hasattr(o, "output_port")
            else o.output_port.id
        )
    )
    consumer_data_product_id = factory.LazyAttribute(
        lambda o: (
            DataProductFactory().id
            if not hasattr(o, "consumer_data_product")
            else o.consumer_data_product.id
        )
    )
    query_count = factory.Faker("random_int", min=0, max=1000)
