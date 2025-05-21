from typing import Optional
from uuid import UUID

from pydantic import Field, computed_field

from app.data_output_configuration.schema_union import DataOutputConfiguration
from app.data_outputs.status import DataOutputStatus
from app.data_outputs_datasets.schema import DataOutputDatasetAssociation
from app.data_products.schema import DataProduct
from app.datasets.schema import Dataset
from app.environment_platform_service_configurations.schema import (
    EnvironmentPlatformServiceConfiguration,
)
from app.platform_services.schema import PlatformService
from app.shared.schema import ORMModel
from app.tags.schema import Tag


class TechnicalInfo(ORMModel):
    environment_id: UUID
    environment: str
    info: Optional[str]


class BaseDataOutputGet(ORMModel):
    id: UUID
    name: str
    description: str
    namespace: str
    owner_id: UUID
    platform_id: UUID
    service_id: UUID
    status: DataOutputStatus

    # Nested schemas
    configuration: DataOutputConfiguration
    owner: DataProduct

    # Excluded
    service: PlatformService = Field(exclude=True)
    environment_configurations: list[EnvironmentPlatformServiceConfiguration] = Field(
        exclude=True
    )

    @computed_field
    def result_string(self) -> str:
        return self.configuration.render_template(self.service.result_string_template)

    @computed_field
    def technical_info(self) -> list[TechnicalInfo]:
        technical_info_list = []
        for environment_configuration in self.environment_configurations:
            configuration = self.configuration.get_configuration(
                environment_configuration.config
            )
            context = configuration.model_dump() if configuration else {}
            context["environment"] = environment_configuration.environment.acronym

            info = self.configuration.render_template(
                self.service.technical_info_template, **context
            )
            technical_info_list.append(
                TechnicalInfo(
                    environment_id=environment_configuration.environment.id,
                    environment=environment_configuration.environment.name,
                    info=info,
                )
            )
        return technical_info_list


class DatasetLink(DataOutputDatasetAssociation):
    # Nested schemas
    dataset: Dataset


class DataOutputGet(BaseDataOutputGet):
    # Nested schemas
    dataset_links: list[DatasetLink]
    tags: list[Tag]


class DataOutputsGet(BaseDataOutputGet):
    pass
