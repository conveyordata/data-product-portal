from typing import Annotated

from pydantic import Field, computed_field

from app.data_product_types.schema import DataProductType
from app.data_products.schema import DataProduct


class DataProductTypeGet(DataProductType):
    data_products: list[DataProduct] = Field(
        ..., description="List of data products associated with the data product type"
    )


class DataProductTypesGet(DataProductType):
    data_products: Annotated[
        list[DataProduct],
        Field(
            exclude=True,
            description="List of data products associated with the data product type",
        ),
    ]

    @computed_field
    def data_product_count(self) -> int:
        return len(self.data_products)
