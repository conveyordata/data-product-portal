from app.data_products.schema_basic import DataProductBasic
from app.datasets.schema_basic import DatasetBasic
from app.domains.schema import Domain


class DomainsGet(Domain):
    data_product_count: int
    dataset_count: int


class DomainGet(Domain):
    data_products: list[DataProductBasic]
    datasets: list[DatasetBasic]
