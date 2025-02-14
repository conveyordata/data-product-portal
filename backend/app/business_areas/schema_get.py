from app.business_areas.schema import BusinessArea
from app.data_products.schema import DataProduct
from app.datasets.schema import Dataset


class BusinessAreasGet(BusinessArea):
    pass


class BusinessAreaGet(BusinessAreasGet):
    data_products: list[DataProduct]
    datasets: list[Dataset]
