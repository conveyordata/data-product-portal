from uuid import UUID

from app.data_product_types.schema_create import DataProductTypeCreate


class DataProductType(DataProductTypeCreate):
    id: UUID
