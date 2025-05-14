from typing import Union

from app.data_outputs_datasets.schema_response import DataOutputDatasetAssociationsGet
from app.data_product_memberships.schema_response import DataProductMembershipsGet
from app.data_products_datasets.schema_response import DataProductDatasetAssociationsGet

PendingAction = Union[
    DataProductDatasetAssociationsGet,
    DataOutputDatasetAssociationsGet,
    DataProductMembershipsGet,
]
