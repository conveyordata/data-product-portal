from typing import Annotated

from pydantic import Field, computed_field

from app.data_products.schema import DataProduct
from app.datasets.schema import Dataset
from app.domains.schema import Domain


class DomainsGet(Domain):
    data_products: Annotated[
        list[DataProduct],
        Field(
            exclude=True, description="List of data products associated with the domain"
        ),
    ]
    datasets: Annotated[
        list[Dataset],
        Field(exclude=True, description="List of datasets associated with the domain"),
    ]

    @computed_field
    def data_product_count(self) -> int:
        return len(self.data_products)

    @computed_field
    def dataset_count(self) -> int:
        return len(self.datasets)


class DomainGet(Domain):
    data_products: list[DataProduct] = Field(
        ..., description="List of data products associated with the domain"
    )
    datasets: list[Dataset] = Field(
        ..., description="List of datasets associated with the domain"
    )
