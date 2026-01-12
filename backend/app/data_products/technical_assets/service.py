import copy
from datetime import datetime
from typing import Sequence
from uuid import UUID

import pytz
from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.authorization.role_assignments.enums import DecisionStatus
from app.configuration.platforms.platform_services.model import PlatformService
from app.configuration.tags.model import Tag as TagModel
from app.configuration.tags.model import ensure_tag_exists
from app.core.namespace.validation import (
    DataOutputNamespaceValidator,
    NamespaceValidityType,
)
from app.data_output_configuration.base_schema import (
    AssetProviderPlugin,
)
from app.data_products.model import DataProduct as DataProductModel
from app.data_products.output_port_technical_assets_link.model import (
    DataOutputDatasetAssociation as DataOutputDatasetAssociationModel,
)
from app.data_products.output_ports.model import Dataset as DatasetModel
from app.data_products.output_ports.model import ensure_dataset_exists
from app.data_products.output_ports.service import DatasetService
from app.data_products.service import DataProductService
from app.data_products.technical_assets.model import DataOutput as DataOutputModel
from app.data_products.technical_assets.model import ensure_data_output_exists
from app.data_products.technical_assets.schema_request import (
    CreateTechnicalAssetRequest,
    DataOutputResultStringRequest,
    DataOutputStatusUpdate,
    DataOutputUpdate,
)
from app.data_products.technical_assets.schema_response import (
    DataOutputGet,
    DataOutputsGet,
    PlatformTile,
    UIElementMetadataResponse,
    UpdateTechnicalAssetResponse,
)
from app.data_products.technical_assets.status import TechnicalAssetStatus
from app.graph.graph import Graph
from app.users.schema import User


class DataOutputService:
    def __init__(self, db: Session):
        self.db = db
        self.namespace_validator = DataOutputNamespaceValidator()

    def _get_tags(self, tag_ids: list[UUID]) -> list[TagModel]:
        tags = []
        for tag_id in tag_ids:
            tag = ensure_tag_exists(tag_id, self.db)
            tags.append(tag)
        return tags

    def get_data_outputs(self) -> Sequence[DataOutputsGet]:
        return (
            self.db.scalars(
                select(DataOutputModel).options(
                    selectinload(DataOutputModel.environment_configurations),
                    selectinload(DataOutputModel.dataset_links)
                    .selectinload(DataOutputDatasetAssociationModel.dataset)
                    .raiseload("*"),
                )
            )
            .unique()
            .all()
        )

    def get_data_output(self, data_product_id: UUID, id: UUID) -> DataOutputGet:
        data_output = self.db.scalar(
            (
                select(DataOutputModel)
                .where(DataOutputModel.id == id)
                .where(DataOutputModel.owner_id == data_product_id)
            ).options(
                selectinload(DataOutputModel.dataset_links),
                selectinload(DataOutputModel.environment_configurations),
            )
        )
        if not data_output:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Technical asset not found",
            )
        return data_output

    def create_data_output(
        self, id: UUID, data_output: CreateTechnicalAssetRequest
    ) -> DataOutputModel:
        if (
            validity := self.namespace_validator.validate_namespace(
                data_output.namespace, self.db, id
            ).validity
        ) != NamespaceValidityType.VALID:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid namespace: {validity.value}",
            )

        if data_output.sourceAligned:
            data_output.status = TechnicalAssetStatus.PENDING
        else:
            data_product = self.db.get(DataProductModel, id)

            data_output.configuration.validate_configuration(data_product)

        data_output_schema = data_output.parse_pydantic_schema()
        tags = self._get_tags(data_output_schema.pop("tag_ids", []))
        model = DataOutputModel(**data_output_schema, tags=tags, owner_id=id)
        self.db.add(model)
        self.db.commit()
        return model

    def remove_data_output(self, data_product_id: UUID, id: UUID) -> DataOutputModel:
        data_output = self.get_data_output_with_links(data_product_id, id)

        result = copy.deepcopy(data_output)
        self.db.delete(data_output)
        self.db.flush()

        self.update_search_vector_associated_datasets(result)
        self.db.commit()
        return result

    def get_data_output_with_links(
        self, data_product_id: UUID, id: UUID
    ) -> DataOutputModel:
        data_output: DataOutputModel | None = self.get_data_output(data_product_id, id)
        if not data_output:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Required data output with {id} does not exist",
            )
        return data_output

    def update_search_vector_associated_datasets(self, result: DataOutputModel):
        dataset_service = DatasetService(self.db)
        for dataset_link in result.dataset_links:
            dataset_service.recalculate_search_vector_for(dataset_link.dataset_id)

    def update_data_output_status(
        self,
        data_product_id: UUID,
        id: UUID,
        data_output: DataOutputStatusUpdate,
        *,
        actor: User,
    ) -> None:
        current_data_output = self.get_data_output_with_links(data_product_id, id)
        current_data_output.status = data_output.status
        self.db.flush()

        self.update_search_vector_associated_datasets(current_data_output)
        self.db.commit()

    def link_dataset_to_data_output(
        self,
        data_product_id: UUID,
        id: UUID,
        dataset_id: UUID,
        *,
        actor: User,
    ) -> DataOutputDatasetAssociationModel:
        dataset = ensure_dataset_exists(
            dataset_id,
            self.db,
            data_product_id=data_product_id,
            options=[selectinload(DatasetModel.data_product_links)],
        )
        data_output = self.get_data_output(data_product_id, id)

        if dataset.id in [
            link.dataset_id
            for link in data_output.dataset_links
            if link.status != DecisionStatus.DENIED
        ]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Dataset {dataset_id} already exists in data product {id}",
            )

        # Data output requests always need to be approved
        dataset_link = DataOutputDatasetAssociationModel(
            dataset_id=dataset_id,
            status=DecisionStatus.PENDING,
            requested_by=actor,
            requested_on=datetime.now(tz=pytz.utc),
        )
        data_output.dataset_links.append(dataset_link)
        self.db.flush()
        DatasetService(self.db).recalculate_search_vector_for(dataset_id)
        self.db.commit()
        return dataset_link

    def unlink_dataset_from_data_output(
        self, data_product_id: UUID, id: UUID, dataset_id: UUID
    ) -> DataOutputModel:
        ensure_dataset_exists(dataset_id, self.db)
        data_output = self.get_data_output(data_product_id, id)

        data_output_dataset = next(
            (
                dataset
                for dataset in data_output.dataset_links
                if dataset.dataset_id == dataset_id
            ),
            None,
        )
        if not data_output_dataset:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Data product dataset for data output {id} not found",
            )

        data_output.dataset_links.remove(data_output_dataset)
        self.db.flush()
        DatasetService(self.db).recalculate_search_vector_for(dataset_id)
        self.db.commit()
        return data_output

    def update_data_output(
        self, data_product_id: UUID, id: UUID, data_output: DataOutputUpdate
    ) -> UpdateTechnicalAssetResponse:
        current_data_output = ensure_data_output_exists(
            id, self.db, data_product_id=data_product_id
        )
        update_data_output = data_output.model_dump(exclude_unset=True)

        for k, v in update_data_output.items():
            if k == "tag_ids":
                new_tags = self._get_tags(v)
                current_data_output.tags = new_tags
            else:
                setattr(current_data_output, k, v) if v else None

        self.db.commit()
        return UpdateTechnicalAssetResponse(id=current_data_output.id)

    def get_graph_data(self, data_product_id: UUID, id: UUID, level: int) -> Graph:
        ensure_data_output_exists(id, self.db, data_product_id=data_product_id)
        graph = DataProductService(self.db).get_graph_data(data_product_id, level)

        for node in graph.nodes:
            if node.isMain:
                node.isMain = False
            if node.id == id:
                node.isMain = True

        return graph

    def get_data_output_result_string(
        self,
        request: DataOutputResultStringRequest,
    ) -> str:
        template = self.db.scalar(
            select(PlatformService.result_string_template).where(
                PlatformService.id == request.service_id,
                PlatformService.platform_id == request.platform_id,
            )
        )

        if not template:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Template not found for the given platform and service",
            )

        return request.configuration.render_template(template)

    def get_technical_asset_ui_metadata(
        self,
    ) -> Sequence[UIElementMetadataResponse]:
        """Generate UI metadata for all registered data output types"""
        data_output_configurations = AssetProviderPlugin.__subclasses__()

        return [
            self._build_metadata_response(plugin)
            for plugin in data_output_configurations
        ]

    def _build_metadata_response(
        self, plugin_class: type[AssetProviderPlugin]
    ) -> UIElementMetadataResponse:
        """Build a complete metadata response for a plugin"""
        platform_meta = plugin_class.get_platform_metadata()
        return UIElementMetadataResponse(
            ui_metadata=plugin_class.get_ui_metadata(),
            plugin=plugin_class.__name__,
            platform=platform_meta.platform_key,
            display_name=platform_meta.display_name,
            icon_name=platform_meta.icon_name,
            parent_platform=platform_meta.parent_platform,
            result_label=platform_meta.result_label,
            result_tooltip=platform_meta.result_tooltip,
        )

    def get_platform_tiles(self, configs: Sequence) -> Sequence[PlatformTile]:
        """Build the complete platform tile structure for the UI"""
        all_metadata = self.get_technical_asset_ui_metadata()

        # Filter to only configured platforms
        configured_metadata = [
            meta for meta in all_metadata if self._has_config(meta, configs)
        ]

        # Build tile hierarchy
        return self._build_tile_hierarchy(configured_metadata)

    def _has_config(self, meta: UIElementMetadataResponse, configs: Sequence) -> bool:
        """Check if a platform has configuration"""
        return any(
            config.service.name.lower() == meta.display_name.lower()
            for config in configs
        )

    def _build_tile_hierarchy(
        self, metadata_list: Sequence[UIElementMetadataResponse]
    ) -> list[PlatformTile]:
        """Organize tiles into parent-child hierarchy"""
        parent_tiles: dict[str, PlatformTile] = {}
        child_tiles: dict[str, list[PlatformTile]] = {}

        for meta in metadata_list:
            tile = PlatformTile(
                label=meta.display_name,
                value=meta.platform,
                icon_name=meta.icon_name,
                has_menu=True,
                has_config=True,
                children=[],
            )

            if meta.parent_platform:
                # Add as child
                child_tiles.setdefault(meta.parent_platform, []).append(tile)

                # Ensure parent exists
                if meta.parent_platform not in parent_tiles:
                    parent_tiles[meta.parent_platform] = PlatformTile(
                        label=meta.parent_platform.upper(),
                        value=meta.parent_platform,
                        icon_name=f"{meta.parent_platform}-logo.svg",
                        has_menu=True,
                        has_config=True,
                        children=[],
                    )
            else:
                # Add as top-level tile
                parent_tiles.setdefault(meta.platform, tile)

        # Attach children to parents
        for parent_key, children in child_tiles.items():
            if parent_key in parent_tiles:
                parent_tiles[parent_key].children = children

        return list(parent_tiles.values())
