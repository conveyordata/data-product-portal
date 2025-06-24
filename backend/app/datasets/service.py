import copy
from typing import Iterable, Sequence
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import asc, select
from sqlalchemy.orm import Session, joinedload, raiseload

from app.core.authz import Authorization
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
from app.datasets.enums import DatasetAccessType
from app.datasets.model import Dataset as DatasetModel
from app.datasets.model import ensure_dataset_exists
from app.datasets.schema_request import (
    DatasetAboutUpdate,
    DatasetCreate,
    DatasetStatusUpdate,
    DatasetUpdate,
)
from app.datasets.schema_response import DatasetGet, DatasetsGet
from app.graph.edge import Edge
from app.graph.graph import Graph
from app.graph.node import Node, NodeData, NodeType
from app.role_assignments.dataset.service import (
    RoleAssignmentService as DatasetRoleAssignmentService,
)
from app.role_assignments.enums import DecisionStatus
from app.tags.model import Tag as TagModel
from app.tags.model import ensure_tag_exists
from app.users.model import User as UserModel
from app.users.schema import User


class DatasetService:
    def __init__(self, db: Session):
        self.db = db
        self.namespace_validator = NamespaceValidator(DatasetModel)

    def get_dataset(self, id: UUID, user: UserModel) -> DatasetGet:
        dataset = self.db.get(
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

        if not self.is_visible_to_user(dataset, user):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have access to this private dataset",
            )

        rolled_up_tags = set()
        for output_link in dataset.data_output_links:
            rolled_up_tags.update(output_link.data_output.tags)

        dataset.rolled_up_tags = rolled_up_tags

        if not dataset.lifecycle:
            default_lifecycle = self.db.scalar(
                select(DataProductLifeCycleModel).where(
                    DataProductLifeCycleModel.is_default
                )
            )
            dataset.lifecycle = default_lifecycle

        return dataset

    def get_datasets(self, user: UserModel) -> Sequence[DatasetsGet]:
        default_lifecycle = self.db.scalar(
            select(DataProductLifeCycleModel).filter(
                DataProductLifeCycleModel.is_default
            )
        )
        datasets = [
            dataset
            for dataset in self.db.scalars(
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
            if self.is_visible_to_user(dataset, user)
        ]

        for dataset in datasets:
            if not dataset.lifecycle:
                dataset.lifecycle = default_lifecycle
        return datasets

    def get_user_datasets(self, user_id: UUID) -> Sequence[DatasetsGet]:
        return (
            self.db.scalars(
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
                .filter(DatasetModel.assignments.any(user_id=user_id))
                .order_by(asc(DatasetModel.name))
            )
            .unique()
            .all()
        )

    def _fetch_tags(self, tag_ids: Iterable[UUID] = ()) -> list[TagModel]:
        tags = []
        for tag_id in tag_ids:
            tag = ensure_tag_exists(tag_id, self.db)
            tags.append(tag)

        return tags

    def create_dataset(self, dataset: DatasetCreate) -> DatasetModel:
        if (
            validity := self.namespace_validator.validate_namespace(
                dataset.namespace, self.db
            ).validity
        ) != NamespaceValidityType.VALID:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid namespace: {validity.value}",
            )

        dataset_schema = dataset.parse_pydantic_schema()
        tags = self._fetch_tags(dataset_schema.pop("tag_ids", []))
        _ = dataset_schema.pop("owners", [])
        model = DatasetModel(**dataset_schema, tags=tags)

        self.db.add(model)
        self.db.commit()
        return model

    def remove_dataset(self, id: UUID) -> DatasetModel:
        dataset = self.db.get(DatasetModel, id)
        if not dataset:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=f"Dataset {id} not found"
            )

        result = copy.deepcopy(dataset)
        self.db.delete(dataset)
        self.db.commit()
        return result

    def update_dataset(self, id: UUID, dataset: DatasetUpdate) -> dict[str, UUID]:
        current_dataset = ensure_dataset_exists(id, self.db)
        updated_dataset = dataset.model_dump(exclude_unset=True)

        if (
            current_dataset.namespace != dataset.namespace
            and (
                validity := self.namespace_validator.validate_namespace(
                    dataset.namespace, self.db
                ).validity
            )
            != NamespaceValidityType.VALID
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid namespace: {validity.value}",
            )

        for k, v in updated_dataset.items():
            if k == "tag_ids":
                new_tags = self._fetch_tags(v)
                current_dataset.tags = new_tags
            else:
                setattr(current_dataset, k, v) if v else None

        self.db.commit()
        return {"id": current_dataset.id}

    def update_dataset_about(
        self,
        id: UUID,
        dataset: DatasetAboutUpdate,
    ) -> None:
        current_dataset = ensure_dataset_exists(id, self.db)
        current_dataset.about = dataset.about
        self.db.commit()

    def update_dataset_status(
        self,
        id: UUID,
        dataset: DatasetStatusUpdate,
    ) -> None:
        current_dataset = ensure_dataset_exists(id, self.db)
        current_dataset.status = dataset.status
        self.db.commit()

    def get_graph_data(self, id: UUID, level: int) -> Graph:
        dataset = self.db.get(
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

    def validate_dataset_namespace(self, namespace: str) -> NamespaceValidation:
        return self.namespace_validator.validate_namespace(namespace, self.db)

    @classmethod
    def dataset_namespace_suggestion(cls, name: str) -> NamespaceSuggestion:
        return NamespaceValidator.namespace_suggestion(name)

    @classmethod
    def dataset_namespace_length_limits(cls) -> NamespaceLengthLimits:
        return NamespaceValidator.namespace_length_limits()

    def is_visible_to_user(self, dataset: DatasetModel, user: User) -> bool:
        if (
            dataset.access_type != DatasetAccessType.PRIVATE
            or Authorization().has_admin_role(user_id=str(user.id))
            or DatasetRoleAssignmentService(self.db).has_assignment(
                dataset_id=dataset.id, user=user
            )
        ):
            return True

        consuming_data_products = {
            link.data_product
            for link in dataset.data_product_links
            if link.status == DecisionStatus.APPROVED
        }

        user_data_products = {
            assignment.data_product
            for assignment in user.data_product_roles
            if assignment.decision == DecisionStatus.APPROVED
        }

        return bool(consuming_data_products & user_data_products)
