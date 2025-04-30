from uuid import UUID

from app.data_products_datasets.enums import DataProductDatasetLinkStatus
from app.shared.schema import ORMModel


class DataProductDatasetAssociationBasic(ORMModel):
    id: UUID
    data_product_id: UUID
    dataset_id: UUID
    status: DataProductDatasetLinkStatus
