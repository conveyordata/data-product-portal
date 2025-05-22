from typing import Optional
from uuid import UUID

from pydantic import Field, computed_field

from app.data_outputs.schema import DataOutput
from app.data_outputs_datasets.schema import DataOutputDatasetAssociation
from app.data_product_lifecycles.schema import DataProductLifeCycle
from app.data_product_settings.schema import (
    DataProductSetting,
    DataProductSettingValue,
    Setting,
)
from app.data_product_types.schema import DataProductType
from app.data_products.status import DataProductStatus
from app.data_products_datasets.schema import DataProductDatasetAssociation
from app.datasets.schema import Dataset
from app.domains.schema import Domain
from app.shared.schema import ORMModel
from app.tags.schema import Tag


class BaseDataProductGet(ORMModel):
    id: UUID
    name: str
    description: str
    namespace: str
    status: DataProductStatus

    # Nested schemas
    tags: list[Tag]
    domain: Domain
    type: DataProductType
    lifecycle: Optional[DataProductLifeCycle]
    data_product_settings: list[DataProductSettingValue] = Field(deprecated=True)

    # Exluded fields
    all_custom_settings: list[DataProductSetting] = Field(exclude=True)

    @computed_field
    def settings(self) -> list[Setting]:
        return [
            next(
                (
                    Setting(
                        **setting.model_dump(),
                        value=setting_value.value,
                        is_default=False
                    )
                    for setting_value in self.data_product_settings
                    if setting_value.data_product_setting_id == setting.id
                ),
                Setting(**setting.model_dump(), value=setting.default, is_default=True),
            )
            for setting in self.all_custom_settings
        ]


class DataOutputLinks(DataOutput):
    # Nested schemas
    dataset_links: list[DataOutputDatasetAssociation]


class DatasetLinks(DataProductDatasetAssociation):
    # Nested schemas
    dataset: Dataset


class DataProductGet(BaseDataProductGet):
    about: Optional[str]

    # Nested schemas
    dataset_links: list[DatasetLinks]
    data_outputs: list[DataOutputLinks]
    rolled_up_tags: set[Tag]


class DataProductsGet(BaseDataProductGet):
    user_count: int
    dataset_count: int
    data_outputs_count: int
