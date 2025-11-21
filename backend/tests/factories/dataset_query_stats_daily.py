import factory

from app.datasets.query_stats_daily.model import DatasetQueryStatsDaily

from .data_product import DataProductFactory
from .dataset import DatasetFactory


class DatasetQueryStatsDailyFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = DatasetQueryStatsDaily

    date = factory.Faker("date_object")
    dataset_id = factory.LazyAttribute(
        lambda o: DatasetFactory().id if not hasattr(o, "dataset") else o.dataset.id
    )
    consumer_data_product_id = factory.LazyAttribute(
        lambda o: (
            DataProductFactory().id
            if not hasattr(o, "consumer_data_product")
            else o.consumer_data_product.id
        )
    )
    query_count = factory.Faker("random_int", min=0, max=1000)
