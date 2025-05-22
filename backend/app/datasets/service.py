from typing import Iterable, Sequence
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import asc, select
from sqlalchemy.orm import Session, joinedload, raiseload

from app.core.aws.refresh_infrastructure_lambda import RefreshInfrastructureLambda
from app.core.namespace.validation import (
    NamespaceLengthLimits,
    NamespaceSuggestion,
    NamespaceValidation,
    NamespaceValidator,
    NamespaceValidityType,
)
from app.data_outputs.model import DataOutput
from app.data_outputs_datasets.model import (
    DataOutputDatasetAssociation as DataOutputDatasetAssociationModel,
)
from app.data_product_lifecycles.model import (
    DataProductLifecycle as DataProductLifeCycleModel,
)
from app.data_products_datasets.model import (
    DataProductDatasetAssociation as DataProductDatasetAssociationModel,
)
from app.datasets.model import Dataset as DatasetModel
from app.datasets.model import ensure_dataset_exists
from app.datasets.schema_request import (
    DatasetAboutUpdate,
    DatasetCreateUpdate,
    DatasetStatusUpdate,
)
from app.datasets.schema_response import DatasetGet, DatasetsGet
from app.graph.edge import Edge
from app.graph.graph import Graph
from app.graph.node import Node, NodeData, NodeType
from app.role_assignments.enums import DecisionStatus
from app.tags.model import Tag as TagModel
from app.tags.model import ensure_tag_exists
from app.users.model import User, ensure_user_exists


class DatasetService:
    def __init__(self):
        self.namespace_validator = NamespaceValidator(DatasetModel)

    def get_dataset(self, id: UUID, db: Session, user: User) -> DatasetGet:
        dataset = db.get(
            DatasetModel,
            id,
            options=[
                joinedload(DatasetModel.data_product_links),
                joinedload(DatasetModel.data_output_links),
            ],
        )

        if not dataset:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Dataset not found"
            )

        if not dataset.is_visible_to_user(user):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have access to this private dataset",
            )

        rolled_up_tags = set()
        for output_link in dataset.data_output_links:
            rolled_up_tags.update(output_link.data_output.tags)

        dataset.rolled_up_tags = rolled_up_tags

        if not dataset.lifecycle:
            default_lifecycle = db.scalar(
                select(DataProductLifeCycleModel).where(
                    DataProductLifeCycleModel.is_default
                )
            )
            dataset.lifecycle = default_lifecycle

        return dataset

    def get_datasets(self, db: Session, user: User) -> Sequence[DatasetsGet]:
        default_lifecycle = db.scalar(
            select(DataProductLifeCycleModel).filter(
                DataProductLifeCycleModel.is_default
            )
        )
        datasets = [
            dataset
            for dataset in db.scalars(
                select(DatasetModel)
                .options(
                    joinedload(DatasetModel.data_product_links)
                    .joinedload(DataProductDatasetAssociationModel.data_product)
                    .raiseload("*"),
                    joinedload(DatasetModel.data_output_links)
                    .joinedload(DataOutputDatasetAssociationModel.data_output)
                    .options(
                        joinedload(DataOutput.configuration),
                        joinedload(DataOutput.owner),
                        raiseload("*"),
                    ),
                )
                .order_by(asc(DatasetModel.name))
            )
            .unique()
            .all()
            if dataset.isVisibleToUser(user)
        ]

        for dataset in datasets:
            if not dataset.lifecycle:
                dataset.lifecycle = default_lifecycle
        return datasets

    def get_user_datasets(self, user_id: UUID, db: Session) -> Sequence[DatasetsGet]:
        return (
            db.scalars(
                select(DatasetModel)
                .options(
                    joinedload(DatasetModel.data_product_links).raiseload("*"),
                    joinedload(DatasetModel.data_output_links)
                    .joinedload(DataOutputDatasetAssociationModel.data_output)
                    .options(
                        joinedload(DataOutput.configuration),
                        joinedload(DataOutput.owner),
                        raiseload("*"),
                    ),
                )
                .filter(DatasetModel.owners.any(id=user_id))
                .order_by(asc(DatasetModel.name))
            )
            .unique()
            .all()
        )

    def _update_owners(
        self, dataset: DatasetCreateUpdate, db: Session, owner_ids: Iterable[UUID] = ()
    ) -> DatasetCreateUpdate:
        if not owner_ids:
            owner_ids = dataset.owners
        dataset.owners = []
        for owner in owner_ids:
            user = ensure_user_exists(owner, db)
            dataset.owners.append(user)
        return dataset

    def _fetch_tags(self, db: Session, tag_ids: Iterable[UUID] = ()) -> list[TagModel]:
        tags = []
        for tag_id in tag_ids:
            tag = ensure_tag_exists(tag_id, db)
            tags.append(tag)

        return tags

    def create_dataset(
        self,
        dataset: DatasetCreateUpdate,
        db: Session,
    ) -> DatasetModel:
        if (
            validity := self.namespace_validator.validate_namespace(
                dataset.namespace, db
            ).validity
        ) != NamespaceValidityType.VALID:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid namespace: {validity.value}",
            )

        new_dataset = self._update_owners(dataset, db)
        dataset_schema = new_dataset.parse_pydantic_schema()
        tags = self._fetch_tags(db, dataset_schema.pop("tag_ids", []))
        model = DatasetModel(**dataset_schema, tags=tags)

        db.add(model)
        db.commit()
        RefreshInfrastructureLambda().trigger()
        return model

    def remove_dataset(self, id: UUID, db: Session) -> None:
        dataset = db.get(DatasetModel, id)
        if not dataset:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=f"Dataset {id} not found"
            )
        db.delete(dataset)
        db.commit()
        RefreshInfrastructureLambda().trigger()

    def update_dataset(
        self, id: UUID, dataset: DatasetCreateUpdate, db: Session
    ) -> dict[str, UUID]:
        current_dataset = ensure_dataset_exists(id, db)
        updated_dataset = dataset.model_dump(exclude_unset=True)

        if (
            current_dataset.namespace != dataset.namespace
            and (
                validity := self.namespace_validator.validate_namespace(
                    dataset.namespace, db
                ).validity
            )
            != NamespaceValidityType.VALID
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid namespace: {validity.value}",
            )

        for k, v in updated_dataset.items():
            if k == "owners":
                current_dataset = self._update_owners(current_dataset, db, v)
            elif k == "tag_ids":
                new_tags = self._fetch_tags(db, v)
                current_dataset.tags = new_tags
            else:
                setattr(current_dataset, k, v) if v else None
        db.commit()
        RefreshInfrastructureLambda().trigger()
        return {"id": current_dataset.id}

    def update_dataset_about(
        self, id: UUID, dataset: DatasetAboutUpdate, db: Session
    ) -> None:
        current_dataset = ensure_dataset_exists(id, db)
        current_dataset.about = dataset.about
        db.commit()

    def update_dataset_status(
        self, id: UUID, dataset: DatasetStatusUpdate, db: Session
    ) -> None:
        current_dataset = ensure_dataset_exists(id, db)
        current_dataset.status = dataset.status
        db.commit()

    def add_user_to_dataset(self, dataset_id: UUID, user_id: UUID, db: Session) -> None:
        dataset = ensure_dataset_exists(dataset_id, db)
        user = ensure_user_exists(user_id, db)
        if user in dataset.owners:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"User {user_id} is already an owner of dataset {dataset_id}",
            )

        dataset.owners.append(user)
        db.commit()
        RefreshInfrastructureLambda().trigger()

    def remove_user_from_dataset(
        self, dataset_id: UUID, user_id: UUID, db: Session
    ) -> None:
        dataset = ensure_dataset_exists(dataset_id, db)
        user = ensure_user_exists(user_id, db)

        if user not in dataset.owners:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"User {user_id} is not an owner of dataset {dataset_id}",
            )
        elif len(dataset.owners) == 1:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot remove the last owner of dataset {dataset_id}",
            )

        dataset.owners.remove(user)
        db.commit()
        RefreshInfrastructureLambda().trigger()

    def get_graph_data(self, id: UUID, level: int, db: Session) -> Graph:
        dataset = db.get(
            DatasetModel,
            id,
            options=[
                joinedload(DatasetModel.data_product_links),
                joinedload(DatasetModel.data_output_links),
            ],
        )
        nodes = [
            Node(
                id=id,
                isMain=True,
                data=NodeData(id=id, name=dataset.name),
                type=NodeType.datasetNode,
            )
        ]
        edges = []
        for downstream_products in dataset.data_product_links:
            nodes.append(
                Node(
                    id=downstream_products.data_product_id,
                    data=NodeData(
                        id=downstream_products.data_product_id,
                        name=downstream_products.data_product.name,
                        icon_key=downstream_products.data_product.type.icon_key,
                    ),
                    type=NodeType.dataProductNode,
                )
            )
            edges.append(
                Edge(
                    id=f"{downstream_products.id}-{dataset.id}",
                    target=downstream_products.data_product_id,
                    source=dataset.id,
                    animated=downstream_products.status == DecisionStatus.APPROVED,
                )
            )

        for data_output_link in dataset.data_output_links:
            data_output = data_output_link.data_output
            nodes.append(
                Node(
                    id=data_output.id,
                    data=NodeData(
                        id=data_output.id,
                        icon_key=data_output.configuration.configuration_type,
                        name=data_output.name,
                        link_to_id=data_output.owner_id,
                    ),
                    type=NodeType.dataOutputNode,
                )
            )
            edges.append(
                Edge(
                    id=f"{data_output.id}-{dataset.id}",
                    source=data_output.id,
                    target=dataset.id,
                    animated=data_output_link.status == DecisionStatus.APPROVED,
                )
            )
            if level >= 2:
                nodes.append(
                    Node(
                        id=f"{data_output.owner.id}_2",
                        data=NodeData(
                            id=f"{data_output.owner.id}",
                            name=data_output.owner.name,
                            icon_key=data_output.owner.type.icon_key,
                        ),
                        type=NodeType.dataProductNode,
                    )
                )
                edges.append(
                    Edge(
                        id=f"{data_output.owner.id}-{data_output.id}-2",
                        target=data_output.id,
                        source=f"{data_output.owner.id}_2",
                        animated=True,
                    )
                )
        return Graph(nodes=set(nodes), edges=set(edges))

    def validate_dataset_namespace(
        self, namespace: str, db: Session
    ) -> NamespaceValidation:
        return self.namespace_validator.validate_namespace(namespace, db)

    def dataset_namespace_suggestion(
        self, name: str, db: Session
    ) -> NamespaceSuggestion:
        return self.namespace_validator.namespace_suggestion(name)

    def dataset_namespace_length_limits(self) -> NamespaceLengthLimits:
        return self.namespace_validator.namespace_length_limits()
