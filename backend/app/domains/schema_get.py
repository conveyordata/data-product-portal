from app.data_products.schema import DataProduct
from app.datasets.schema import Dataset
from app.domains.schema import Domain


class DomainsGet(Domain):
    data_product_count: int
    dataset_count: int


class DomainGet(Domain):
    data_products: list[DataProduct]
    datasets: list[Dataset]
