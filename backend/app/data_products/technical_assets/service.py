import copy
from datetime import datetime
from typing import Sequence
from uuid import UUID

import pytz
from fastapi import Depends, HTTPException, status
from sqlalchemy import delete, select
from sqlalchemy.orm import Session, joinedload, selectinload

from app.authorization.role_assignments.enums import DecisionStatus
from app.configuration.access_modes.model import AccessMode as AccessModeModel
from app.configuration.environments.model import Environment as EnvironmentModel
from app.configuration.tags.model import Tag as TagModel
from app.configuration.tags.model import ensure_tag_exists
from app.core import context
from app.core.namespace.validation import (
    TechnicalAssetNamespaceValidator,
)
from app.core.webhooks.events import (
    TechnicalAssetEnvironmentConfigurationAppliedEvent,
)
from app.data_products.model import DataProduct as DataProductModel
from app.data_products.model import ensure_data_product_exists
from app.data_products.output_port_technical_assets_link.model import (
    TechnicalAssetOutputPortAssociation,
)
from app.data_products.output_port_technical_assets_link.model import (
    TechnicalAssetOutputPortAssociation as TechnicalAssetOutputPortAssociationModel,
)
from app.data_products.output_ports.model import OutputPort as OutputPortModel
from app.data_products.output_ports.model import ensure_output_port_exists
from app.data_products.output_ports.service import OutputPortService
from app.data_products.service import DataProductService
from app.data_products.technical_assets.enums import TechnicalMapping
from app.data_products.technical_assets.model import (
    TechnicalAsset as TechnicalAssetModel,
)
from app.data_products.technical_assets.model import (
    TechnicalAssetEnvironmentOverride,
    ensure_technical_asset_exists,
)
from app.data_products.technical_assets.schema_request import (
    CreateTechnicalAssetRequest,
    TechnicalAssetStatusUpdate,
    TechnicalAssetUpdate,
    UpdateTechnicalAssetEnvironmentConfigurationRequest,
)
from app.data_products.technical_assets.schema_response import (
    EnvironmentConfigurationProperty,
    EnvironmentConfigurationValue,
    GetTechnicalAssetEnvironmentConfigurationResponse,
    UpdateTechnicalAssetResponse,
)
from app.data_products.technical_assets.status import TechnicalAssetStatus
from app.database.deps import get_db_session
from app.graph.graph import Graph
from app.plugins.registry import plugin_registry
from app.resource_names.service import ResourceNameValidityType
from app.technical_asset_configuration.base_schema import (
    EnvOverridableProperty,
    PluginContext,
)
from app.users.schema import User

TECHNICAL_ASSET_ACCESS_MODES_INCOMPATIBLE_ERROR = HTTPException(
    status_code=status.HTTP_409_CONFLICT,
    detail="Access modes of technical asset are incompatible with access modes of output port",
)

TECHNICAL_ASSET_ALREADY_LINKED_ERROR = HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST,
    detail="Technical Asset already exists in output port",
)

TECHNICAL_ASSET_NOT_ACTIVE_ERROR = HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST,
    detail="Cannot link technical asset that is not active",
)

TECHNICAL_ASSET_NOT_SHAREABLE_ERROR = HTTPException(
    status_code=status.HTTP_409_CONFLICT,
    detail="Technical assets of this type are not shareable and cannot be linked to an Output Port",
)


def ensure_technical_asset_shareable(technical_asset: TechnicalAssetModel) -> None:
    plugin = plugin_registry.get(technical_asset.configuration.configuration_type)
    if not plugin.get_platform_metadata().shareable:
        raise TECHNICAL_ASSET_NOT_SHAREABLE_ERROR


class TechnicalAssetService:
    def __init__(self, db: Session = Depends(get_db_session, scope="function")):
        self.db = db
        self.namespace_validator = TechnicalAssetNamespaceValidator()

    def _get_tags(self, tag_ids: list[UUID]) -> list[TagModel]:
        tags = []
        for tag_id in tag_ids:
            tag = ensure_tag_exists(tag_id, self.db)
            tags.append(tag)
        return tags

    def _get_access_modes(
        self, access_mode_ids: list[UUID], technical_asset_type
    ) -> list[AccessModeModel]:
        access_modes = self.db.scalars(
            select(AccessModeModel).where(AccessModeModel.id.in_(access_mode_ids))
        ).all()
        if len(access_mode_ids) != len(access_modes):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid access modes provided",
            )
        for access_mode in access_modes:
            if technical_asset_type not in access_mode.technical_asset_types:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Access mode {access_mode.name} is not compatible with technical asset type {technical_asset_type}",
                )
        return access_modes

    @staticmethod
    def get_status_for(technical_mapping: TechnicalMapping):
        if technical_mapping == TechnicalMapping.Default:
            return TechnicalAssetStatus.ACTIVE
        return TechnicalAssetStatus.PENDING

    def _filter_environment_configurations_by_data_product(
        self, technical_assets: Sequence[TechnicalAssetModel]
    ) -> None:
        for technical_asset in technical_assets:
            allowed_environment_ids = {
                declaration.environment_id
                for declaration in technical_asset.owner.environments
            }
            technical_asset.environment_configurations = [
                config
                for config in technical_asset.environment_configurations
                if config.environment_id in allowed_environment_ids
            ]

    def get_technical_assets(self) -> Sequence[TechnicalAssetModel]:
        technical_assets = (
            self.db.scalars(
                select(TechnicalAssetModel).options(
                    selectinload(TechnicalAssetModel.environment_configurations),
                    joinedload(TechnicalAssetModel.owner).selectinload(
                        DataProductModel.environments
                    ),
                    selectinload(TechnicalAssetModel.output_port_links)
                    .selectinload(TechnicalAssetOutputPortAssociationModel.output_port)
                    .raiseload("*"),
                )
            )
            .unique()
            .all()
        )
        self._filter_environment_configurations_by_data_product(technical_assets)
        return technical_assets

    def get_technical_asset(
        self, data_product_id: UUID, id: UUID
    ) -> TechnicalAssetModel:
        technical_asset = self.db.scalar(
            (
                select(TechnicalAssetModel)
                .where(TechnicalAssetModel.id == id)
                .where(TechnicalAssetModel.owner_id == data_product_id)
            ).options(
                selectinload(TechnicalAssetModel.output_port_links),
                selectinload(TechnicalAssetModel.environment_configurations),
                joinedload(TechnicalAssetModel.owner).selectinload(
                    DataProductModel.environments
                ),
            )
        )
        if not technical_asset:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Technical asset not found",
            )
        self._filter_environment_configurations_by_data_product([technical_asset])
        return technical_asset

    def create_technical_asset(
        self, data_product_id: UUID, technical_asset: CreateTechnicalAssetRequest
    ) -> TechnicalAssetModel:
        if (
            validity := self.namespace_validator.validate_namespace(
                technical_asset.namespace, self.db, data_product_id
            ).validity
        ) != ResourceNameValidityType.VALID:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid namespace: {validity.value}",
            )

        if technical_asset.technical_mapping == TechnicalMapping.Default:
            technical_asset.configuration.validate_configuration(
                PluginContext.build(
                    ensure_data_product_exists(data_product_id, self.db),
                    technical_asset.namespace,
                    TechnicalMapping.Default,
                ),
                self.db,
            )

        technical_asset_schema = technical_asset.parse_pydantic_schema()
        tags = self._get_tags(technical_asset_schema.pop("tag_ids", []))
        access_modes = self._get_access_modes(
            technical_asset_schema.pop("access_mode_ids", []),
            technical_asset.configuration.name,
        )
        technical_asset_schema.pop("sourceAligned")  # Remove deprecated field

        technical_asset_status = self.get_status_for(technical_asset.technical_mapping)  # type: ignore[arg-type]
        model = TechnicalAssetModel(
            **technical_asset_schema,
            tags=tags,
            access_modes=access_modes,
            owner_id=data_product_id,
            status=technical_asset_status,
        )
        self.db.add(model)
        self.db.flush()
        return model

    def remove_technical_asset(
        self, data_product_id: UUID, id: UUID
    ) -> TechnicalAssetModel:
        technical_asset = self.get_technical_asset_with_links(data_product_id, id)

        result = copy.deepcopy(technical_asset)
        self.db.delete(technical_asset)
        self.db.flush()

        self.update_search_for_associated_datasets(result)
        self.db.flush()
        return result

    def get_technical_asset_with_links(
        self, data_product_id: UUID, id: UUID
    ) -> TechnicalAssetModel:
        technical_asset: TechnicalAssetModel | None = self.get_technical_asset(
            data_product_id, id
        )
        if not technical_asset:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Required technical asset with {id} does not exist",
            )
        return technical_asset

    def update_search_for_associated_datasets(self, result: TechnicalAssetModel):
        dataset_service = OutputPortService(self.db)
        for dataset_link in result.output_port_links:
            dataset_service.recalculate_search(dataset_link.output_port_id)

    def update_technical_asset_status(
        self,
        data_product_id: UUID,
        id: UUID,
        technical_asset_update: TechnicalAssetStatusUpdate,
        *,
        actor: User,
    ) -> None:
        current_technical_asset = self.get_technical_asset_with_links(
            data_product_id, id
        )
        current_technical_asset.status = technical_asset_update.status
        self.db.flush()

        self.update_search_for_associated_datasets(current_technical_asset)
        self.db.flush()

    def link_output_port_to_technical_asset(
        self,
        data_product_id: UUID,
        id: UUID,
        output_port_id: UUID,
        *,
        actor: User,
    ) -> TechnicalAssetOutputPortAssociationModel:
        output_port = ensure_output_port_exists(
            output_port_id,
            self.db,
            data_product_id=data_product_id,
            options=[
                selectinload(OutputPortModel.data_product_links),
            ],
        )
        technical_asset = self.get_technical_asset(data_product_id, id)
        if technical_asset.status != TechnicalAssetStatus.ACTIVE:
            raise TECHNICAL_ASSET_NOT_ACTIVE_ERROR
        ensure_technical_asset_shareable(technical_asset)

        if output_port.id in [
            link.output_port_id
            for link in technical_asset.output_port_links
            if link.status != DecisionStatus.DENIED
        ]:
            raise TECHNICAL_ASSET_ALREADY_LINKED_ERROR
        if (
            technical_asset.access_modes
            and output_port.access_modes
            and set(output_port.access_modes) != set(technical_asset.access_modes)
        ):
            raise TECHNICAL_ASSET_ACCESS_MODES_INCOMPATIBLE_ERROR

        # Data output requests always need to be approved
        output_port_link = TechnicalAssetOutputPortAssociationModel(
            output_port_id=output_port_id,
            status=DecisionStatus.PENDING,
            requested_by=actor,
            requested_on=datetime.now(tz=pytz.utc),
        )
        technical_asset.output_port_links.append(output_port_link)
        self.db.flush()
        OutputPortService(self.db).recalculate_search(output_port_id)
        return output_port_link

    def unlink_output_port_from_technical_asset(
        self, data_product_id: UUID, id: UUID, output_port_id: UUID
    ) -> TechnicalAssetModel:
        ensure_output_port_exists(output_port_id, self.db)
        technical_asset = self.get_technical_asset(data_product_id, id)

        link = next(
            (
                dataset
                for dataset in technical_asset.output_port_links
                if dataset.output_port_id == output_port_id
            ),
            None,
        )
        if not link:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Data product output port for technical asset {id} not found",
            )

        technical_asset.output_port_links.remove(link)
        self.db.flush()
        OutputPortService(self.db).recalculate_search(output_port_id)
        self.db.flush()
        return technical_asset

    def update_technical_asset(
        self, data_product_id: UUID, id: UUID, technical_asset: TechnicalAssetUpdate
    ) -> UpdateTechnicalAssetResponse:
        current_technical_asset = ensure_technical_asset_exists(
            id, self.db, data_product_id=data_product_id
        )
        update_technical_asset = technical_asset.model_dump(exclude_unset=True)

        for k, v in update_technical_asset.items():
            if k == "tag_ids":
                new_tags = self._get_tags(v)
                current_technical_asset.tags = new_tags
            else:
                setattr(current_technical_asset, k, v) if v else None

        self.db.flush()
        return UpdateTechnicalAssetResponse(id=current_technical_asset.id)

    def get_environment_configuration(
        self, data_product_id: UUID, id: UUID
    ) -> GetTechnicalAssetEnvironmentConfigurationResponse:
        return self._environment_configuration(
            self.get_technical_asset(data_product_id, id)
        )

    def update_environment_configuration(
        self,
        data_product_id: UUID,
        id: UUID,
        request: UpdateTechnicalAssetEnvironmentConfigurationRequest,
    ) -> GetTechnicalAssetEnvironmentConfigurationResponse:
        technical_asset = self.get_technical_asset(data_product_id, id)
        overridable = {
            prop.name: prop
            for prop in self._env_overridable_properties(technical_asset)
        }
        self._validate_values(overridable, request.base_values)
        for environment_id, values in request.overrides.items():
            self._ensure_data_product_environment(technical_asset, environment_id)
            self._validate_values(overridable, values)

        for name, value in request.base_values.items():
            setattr(technical_asset.configuration, name, value)
        self.db.execute(
            delete(TechnicalAssetEnvironmentOverride).where(
                TechnicalAssetEnvironmentOverride.technical_asset_id == id
            )
        )
        self.db.add_all(
            [
                TechnicalAssetEnvironmentOverride(
                    technical_asset_id=id,
                    environment_id=environment_id,
                    property=name,
                    value=value,
                )
                for environment_id, values in request.overrides.items()
                for name, value in values.items()
            ]
        )
        self.db.flush()
        return self._environment_configuration(technical_asset)

    def apply_environment_configuration(
        self, data_product_id: UUID, id: UUID, environment_id: UUID
    ) -> None:
        technical_asset = self.get_technical_asset(data_product_id, id)
        environment = self._ensure_data_product_environment(
            technical_asset, environment_id
        )
        context.queue_event(
            TechnicalAssetEnvironmentConfigurationAppliedEvent(
                id=id,
                data_product_id=data_product_id,
                environment=environment.acronym,
                configuration={
                    prop.name: value.effective_value
                    for prop in self._environment_configuration(
                        technical_asset
                    ).properties
                    for value in prop.environments
                    if value.environment_id == environment_id
                },
            )
        )

    def _environment_configuration(
        self, technical_asset: TechnicalAssetModel
    ) -> GetTechnicalAssetEnvironmentConfigurationResponse:
        overrides = {
            (override.environment_id, override.property): override.value
            for override in self.db.scalars(
                select(TechnicalAssetEnvironmentOverride).where(
                    TechnicalAssetEnvironmentOverride.technical_asset_id
                    == technical_asset.id
                )
            )
        }
        properties = []
        for prop in self._env_overridable_properties(technical_asset):
            base_value = (
                getattr(technical_asset.configuration, prop.name) or prop.default
            )
            properties.append(
                EnvironmentConfigurationProperty(
                    name=prop.name,
                    label=prop.label,
                    allowed_values=prop.allowed_values,
                    default=prop.default,
                    base_value=base_value,
                    environments=[
                        EnvironmentConfigurationValue(
                            environment_id=item.environment_id,
                            name=item.environment.name,
                            acronym=item.environment.acronym,
                            override=(
                                override := overrides.get(
                                    (item.environment_id, prop.name)
                                )
                            ),
                            effective_value=override or base_value,
                        )
                        for item in technical_asset.owner.environments
                    ],
                )
            )
        return GetTechnicalAssetEnvironmentConfigurationResponse(properties=properties)

    @staticmethod
    def _env_overridable_properties(
        technical_asset: TechnicalAssetModel,
    ) -> list[EnvOverridableProperty]:
        return plugin_registry.get(
            technical_asset.configuration.configuration_type
        ).env_overridable_properties

    @staticmethod
    def _ensure_data_product_environment(
        technical_asset: TechnicalAssetModel, environment_id: UUID
    ) -> EnvironmentModel:
        environment = next(
            (
                item.environment
                for item in technical_asset.owner.environments
                if item.environment_id == environment_id
            ),
            None,
        )
        if environment is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Environment {environment_id} is not an environment of the Data Product",
            )
        return environment

    @staticmethod
    def _validate_values(
        overridable: dict[str, EnvOverridableProperty], values: dict[str, str]
    ) -> None:
        for name, value in values.items():
            if name not in overridable:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Property '{name}' is not overridable per environment",
                )
            allowed_values = overridable[name].allowed_values
            if value not in allowed_values:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Value '{value}' is not allowed for '{name}', allowed values: {', '.join(allowed_values)}",
                )

    def get_graph_data(self, data_product_id: UUID, id: UUID, level: int) -> Graph:
        ensure_technical_asset_exists(id, self.db, data_product_id=data_product_id)
        graph = DataProductService(self.db).get_graph_data(data_product_id, level)

        for node in graph.nodes:
            if node.isMain:
                node.isMain = False
            if node.id == id:
                node.isMain = True

        return graph

    def get_technical_assets_for_data_product(
        self, data_product_id: UUID
    ) -> Sequence[TechnicalAssetModel]:
        technical_assets = (
            self.db.scalars(
                select(TechnicalAssetModel)
                .options(
                    selectinload(TechnicalAssetModel.environment_configurations),
                    joinedload(TechnicalAssetModel.owner).selectinload(
                        DataProductModel.environments
                    ),
                    selectinload(TechnicalAssetModel.output_port_links)
                    .selectinload(TechnicalAssetOutputPortAssociation.output_port)
                    .selectinload(OutputPortModel.tags)
                    .raiseload("*"),
                )
                .filter(TechnicalAssetModel.owner_id == data_product_id)
            )
            .unique()
            .all()
        )
        self._filter_environment_configurations_by_data_product(technical_assets)
        return technical_assets
