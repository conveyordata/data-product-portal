import copy
from datetime import datetime
from typing import Sequence
from uuid import UUID

import pytz
from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.authorization.role_assignments.enums import DecisionStatus
from app.configuration.tags.model import Tag as TagModel
from app.configuration.tags.model import ensure_tag_exists
from app.core.namespace.validation import (
    TechnicalAssetNamespaceValidator,
)
from app.data_products.model import DataProduct as DataProductModel
from app.data_products.output_port_technical_assets_link.model import (
    DataOutputDatasetAssociation,
)
from app.data_products.output_port_technical_assets_link.model import (
    DataOutputDatasetAssociation as DataOutputDatasetAssociationModel,
)
from app.data_products.output_ports.model import OutputPort as OutputPortModel
from app.data_products.output_ports.model import ensure_output_port_exists
from app.data_products.output_ports.service import OutputPortService
from app.data_products.service import DataProductService
from app.data_products.technical_assets.enums import TechnicalMapping
from app.data_products.technical_assets.model import (
    TechnicalAsset as TechnicalAssetModel,
)
from app.data_products.technical_assets.model import ensure_technical_asset_exists
from app.data_products.technical_assets.schema_request import (
    CreateTechnicalAssetRequest,
    DataOutputStatusUpdate,
    DataOutputUpdate,
)
from app.data_products.technical_assets.schema_response import (
    UpdateTechnicalAssetResponse,
)
from app.data_products.technical_assets.status import TechnicalAssetStatus
from app.graph.graph import Graph
from app.resource_names.service import ResourceNameValidityType
from app.users.schema import User


class DataOutputService:
    def __init__(self, db: Session):
        self.db = db
        self.namespace_validator = TechnicalAssetNamespaceValidator()

    def _get_tags(self, tag_ids: list[UUID]) -> list[TagModel]:
        tags = []
        for tag_id in tag_ids:
            tag = ensure_tag_exists(tag_id, self.db)
            tags.append(tag)
        return tags

    @staticmethod
    def get_status_for(technical_mapping: TechnicalMapping):
        if technical_mapping == TechnicalMapping.Default:
            return TechnicalAssetStatus.ACTIVE
        return TechnicalAssetStatus.PENDING

    def get_data_outputs(self) -> Sequence[TechnicalAssetModel]:
        return (
            self.db.scalars(
                select(TechnicalAssetModel).options(
                    selectinload(TechnicalAssetModel.environment_configurations),
                    selectinload(TechnicalAssetModel.dataset_links)
                    .selectinload(DataOutputDatasetAssociationModel.output_port)
                    .raiseload("*"),
                )
            )
            .unique()
            .all()
        )

    def get_technical_asset(
        self, data_product_id: UUID, id: UUID
    ) -> TechnicalAssetModel:
        technical_asset = self.db.scalar(
            (
                select(TechnicalAssetModel)
                .where(TechnicalAssetModel.id == id)
                .where(TechnicalAssetModel.owner_id == data_product_id)
            ).options(
                selectinload(TechnicalAssetModel.dataset_links),
                selectinload(TechnicalAssetModel.environment_configurations),
            )
        )
        if not technical_asset:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Technical asset not found",
            )
        return technical_asset

    def create_technical_asset(
        self, id: UUID, technical_asset: CreateTechnicalAssetRequest
    ) -> TechnicalAssetModel:
        if (
            validity := self.namespace_validator.validate_namespace(
                technical_asset.namespace, self.db, id
            ).validity
        ) != ResourceNameValidityType.VALID:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid namespace: {validity.value}",
            )

        if technical_asset.technical_mapping == TechnicalMapping.Default:
            data_product = self.db.get(DataProductModel, id)
            technical_asset.configuration.validate_configuration(data_product, self.db)

        data_output_schema = technical_asset.parse_pydantic_schema()
        tags = self._get_tags(data_output_schema.pop("tag_ids", []))
        data_output_schema.pop("sourceAligned")  # Remove deprecated field

        technical_asset_status = self.get_status_for(technical_asset.technical_mapping)  # type: ignore[arg-type]
        model = TechnicalAssetModel(
            **data_output_schema,
            tags=tags,
            owner_id=id,
            status=technical_asset_status,
        )
        self.db.add(model)
        self.db.commit()
        return model

    def remove_data_output(
        self, data_product_id: UUID, id: UUID
    ) -> TechnicalAssetModel:
        data_output = self.get_data_output_with_links(data_product_id, id)

        result = copy.deepcopy(data_output)
        self.db.delete(data_output)
        self.db.flush()

        self.update_search_for_associated_datasets(result)
        self.db.commit()
        return result

    def get_data_output_with_links(
        self, data_product_id: UUID, id: UUID
    ) -> TechnicalAssetModel:
        data_output: TechnicalAssetModel | None = self.get_technical_asset(
            data_product_id, id
        )
        if not data_output:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Required data output with {id} does not exist",
            )
        return data_output

    def update_search_for_associated_datasets(self, result: TechnicalAssetModel):
        dataset_service = OutputPortService(self.db)
        for dataset_link in result.dataset_links:
            dataset_service.recalculate_search(dataset_link.output_port_id)

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

        self.update_search_for_associated_datasets(current_data_output)
        self.db.commit()

    def link_dataset_to_data_output(
        self,
        data_product_id: UUID,
        id: UUID,
        output_port_id: UUID,
        *,
        actor: User,
    ) -> DataOutputDatasetAssociationModel:
        output_port = ensure_output_port_exists(
            output_port_id,
            self.db,
            data_product_id=data_product_id,
            options=[
                selectinload(OutputPortModel.data_product_links),
                selectinload(OutputPortModel.data_output_links).selectinload(
                    DataOutputDatasetAssociationModel.data_output
                ),
            ],
        )
        technical_asset = self.get_technical_asset(data_product_id, id)
        if technical_asset.status != TechnicalAssetStatus.ACTIVE:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot link technical asset that is not active",
            )

        if output_port.id in [
            link.output_port_id
            for link in technical_asset.dataset_links
            if link.status != DecisionStatus.DENIED
        ]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Technical Asset {id} already exists in output port {output_port_id}",
            )
        if (
            technical_asset.access_modes
            and output_port.access_modes
            and sorted(output_port.access_modes, key=lambda am: am.name)
            != sorted(technical_asset.access_modes, key=lambda am: am.name)
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Access modes of technical asset {id} are incompatible with access modes of technical assets already part of output port {output_port_id}",
            )

        # Data output requests always need to be approved
        output_port_link = DataOutputDatasetAssociationModel(
            output_port_id=output_port_id,
            status=DecisionStatus.PENDING,
            requested_by=actor,
            requested_on=datetime.now(tz=pytz.utc),
        )
        technical_asset.dataset_links.append(output_port_link)
        self.db.flush()
        OutputPortService(self.db).recalculate_search(output_port_id)
        return output_port_link

    def unlink_dataset_from_data_output(
        self, data_product_id: UUID, id: UUID, output_port_id: UUID
    ) -> TechnicalAssetModel:
        ensure_output_port_exists(output_port_id, self.db)
        data_output = self.get_technical_asset(data_product_id, id)

        data_output_dataset = next(
            (
                dataset
                for dataset in data_output.dataset_links
                if dataset.output_port_id == output_port_id
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
        OutputPortService(self.db).recalculate_search(output_port_id)
        self.db.commit()
        return data_output

    def update_data_output(
        self, data_product_id: UUID, id: UUID, data_output: DataOutputUpdate
    ) -> UpdateTechnicalAssetResponse:
        current_data_output = ensure_technical_asset_exists(
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
        return (
            self.db.scalars(
                select(TechnicalAssetModel)
                .options(
                    selectinload(TechnicalAssetModel.environment_configurations),
                    selectinload(TechnicalAssetModel.dataset_links)
                    .selectinload(DataOutputDatasetAssociation.output_port)
                    .selectinload(OutputPortModel.tags)
                    .raiseload("*"),
                )
                .filter(TechnicalAssetModel.owner_id == data_product_id)
            )
            .unique()
            .all()
        )
