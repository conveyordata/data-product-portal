from datetime import datetime
from typing import Optional, Sequence
from uuid import UUID

import pytz
from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.core.aws.refresh_infrastructure_lambda import RefreshInfrastructureLambda
from app.core.namespace.validation import (
    DataOutputNamespaceValidator,
    NamespaceLengthLimits,
    NamespaceSuggestion,
    NamespaceValidator,
    NamespaceValidityType,
)
from app.data_outputs.model import DataOutput as DataOutputModel
from app.data_outputs.schema_request import (
    DataOutputCreate,
    DataOutputStatusUpdate,
    DataOutputUpdate,
)
from app.data_outputs.schema_response import DataOutputGet, DataOutputsGet
from app.data_outputs.status import DataOutputStatus
from app.data_outputs_datasets.model import (
    DataOutputDatasetAssociation as DataOutputDatasetAssociationModel,
)
from app.data_products.model import DataProduct as DataProductModel
from app.data_products.service import DataProductService
from app.database.database import ensure_exists
from app.datasets.model import Dataset as DatasetModel
from app.datasets.model import ensure_dataset_exists
from app.graph.graph import Graph
from app.role_assignments.enums import DecisionStatus
from app.tags.model import Tag as TagModel
from app.tags.model import ensure_tag_exists
from app.users.schema import User


class DataOutputService:
    def __init__(self, db: Session):
        self.db = db
        self.namespace_validator = DataOutputNamespaceValidator()

    def ensure_data_output_exists(
        self, data_output_id: UUID, **kwargs
    ) -> DataOutputModel:
        return ensure_exists(data_output_id, self.db, DataOutputModel, **kwargs)

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
                    joinedload(DataOutputModel.dataset_links)
                    .joinedload(DataOutputDatasetAssociationModel.dataset)
                    .raiseload("*"),
                )
            )
            .unique()
            .all()
        )

    def get_data_output(self, id: UUID) -> Optional[DataOutputGet]:
        return self.db.get(
            DataOutputModel, id, options=[joinedload(DataOutputModel.dataset_links)]
        )

    def create_data_output(
        self,
        id: UUID,
        data_output: DataOutputCreate,
    ) -> dict[str, UUID]:
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
            data_output.status = DataOutputStatus.PENDING
        else:
            data_product = self.db.get(DataProductModel, id)

            # TODO Figure out if this validation needs to happen either way
            # somehow and let sourcealigned be handled internally there?
            data_output.configuration.validate_configuration(data_product)

        data_output_schema = data_output.parse_pydantic_schema()
        tags = self._get_tags(data_output_schema.pop("tag_ids", []))
        model = DataOutputModel(**data_output_schema, tags=tags, owner_id=id)

        self.db.add(model)
        self.db.commit()
        RefreshInfrastructureLambda().trigger()
        return {"id": model.id}

    def remove_data_output(self, id: UUID) -> None:
        data_output = self.db.get(
            DataOutputModel,
            id,
        )
        if not data_output:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Data Output {id} not found",
            )

        self.db.delete(data_output)
        self.db.commit()
        RefreshInfrastructureLambda().trigger()

    def update_data_output_status(
        self, id: UUID, data_output: DataOutputStatusUpdate
    ) -> None:
        current_data_output = self.ensure_data_output_exists(id)
        current_data_output.status = data_output.status
        self.db.commit()

    def link_dataset_to_data_output(
        self,
        id: UUID,
        dataset_id: UUID,
        authenticated_user: User,
    ) -> DataOutputDatasetAssociationModel:
        dataset = ensure_dataset_exists(
            dataset_id, self.db, options=[joinedload(DatasetModel.data_product_links)]
        )
        data_output = self.ensure_data_output_exists(
            id, options=[joinedload(DataOutputModel.dataset_links)]
        )

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
            requested_by=authenticated_user,
            requested_on=datetime.now(tz=pytz.utc),
        )
        data_output.dataset_links.append(dataset_link)

        self.db.commit()
        self.db.refresh(data_output)
        RefreshInfrastructureLambda().trigger()
        return dataset_link

    def unlink_dataset_from_data_output(self, id: UUID, dataset_id: UUID) -> None:
        ensure_dataset_exists(dataset_id, self.db)
        data_output = self.ensure_data_output_exists(
            id, options=[joinedload(DataOutputModel.dataset_links)]
        )

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

        self.db.commit()
        RefreshInfrastructureLambda().trigger()

    def update_data_output(
        self, id: UUID, data_output: DataOutputUpdate
    ) -> dict[str, UUID]:
        current_data_output = self.ensure_data_output_exists(id)
        update_data_output = data_output.model_dump(exclude_unset=True)

        for k, v in update_data_output.items():
            if k == "tag_ids":
                new_tags = self._get_tags(v)
                current_data_output.tags = new_tags
            else:
                setattr(current_data_output, k, v) if v else None

        self.db.commit()
        RefreshInfrastructureLambda().trigger()
        return {"id": current_data_output.id}

    def get_graph_data(self, id: UUID, level: int) -> Graph:
        data_output = self.db.get(DataOutputModel, id)
        graph = DataProductService().get_graph_data(
            data_output.owner_id, level, self.db
        )

        for node in graph.nodes:
            if node.isMain:
                node.isMain = False
            if node.id == id:
                node.isMain = True

        return graph

    @classmethod
    def data_output_namespace_suggestion(cls, name: str) -> NamespaceSuggestion:
        return NamespaceValidator.namespace_suggestion(name)

    @classmethod
    def data_output_namespace_length_limits(cls) -> NamespaceLengthLimits:
        return NamespaceValidator.namespace_length_limits()
