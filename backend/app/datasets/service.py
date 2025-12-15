import copy
from typing import Iterable, Optional, Sequence
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import asc, desc, func, select
from sqlalchemy.orm import Session, joinedload, raiseload, selectinload

from app.authorization.role_assignments.enums import DecisionStatus
from app.authorization.role_assignments.output_port.service import (
    RoleAssignmentService as DatasetRoleAssignmentService,
)
from app.configuration.data_product_lifecycles.model import (
    DataProductLifecycle as DataProductLifeCycleModel,
)
from app.configuration.tags.model import Tag as TagModel
from app.configuration.tags.model import ensure_tag_exists
from app.core.authz import Authorization
from app.core.logging import logger
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
from app.data_products_datasets.model import (
    DataProductDatasetAssociation as DataProductDatasetAssociationModel,
)
from app.datasets.enums import OutputPortAccessType
from app.datasets.model import Dataset as DatasetModel
from app.datasets.model import ensure_dataset_exists
from app.datasets.schema_request import (
    DatasetAboutUpdate,
    DatasetCreate,
    DatasetStatusUpdate,
    DatasetUpdate,
    DatasetUsageUpdate,
)
from app.datasets.schema_response import (
    DatasetEmbed,
    DatasetGet,
    DatasetsGet,
    DatasetsSearch,
)
from app.datasets.search_dataset import (
    recalculate_search_vector_dataset_statement,
    recalculate_search_vector_datasets_statement,
)
from app.graph.edge import Edge
from app.graph.graph import Graph
from app.graph.node import Node, NodeData, NodeType
from app.settings import settings
from app.users.model import User as UserModel
from app.users.schema import User


def get_dataset_load_options():
    return [
        selectinload(DatasetModel.data_product_links)
        .selectinload(DataProductDatasetAssociationModel.data_product)
        .raiseload("*"),
        selectinload(DatasetModel.data_output_links)
        .selectinload(DataOutputDatasetAssociationModel.data_output)
        .options(
            joinedload(DataOutput.configuration),
            joinedload(DataOutput.owner),
            raiseload("*"),
        ),
    ]


class DatasetService:
    def __init__(self, db: Session):
        self.db = db
        self.namespace_validator = NamespaceValidator(DatasetModel)

    def get_dataset(self, id: UUID, user: UserModel) -> DatasetGet:
        dataset = self.db.get(
            DatasetModel,
            id,
            options=[
                selectinload(DatasetModel.data_product_links),
                selectinload(DatasetModel.data_output_links),
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

    def search_datasets(
        self, query: str, limit: int, user: UserModel
    ) -> Sequence[DatasetsSearch]:
        load_options = get_dataset_load_options()
        stmt = (
            select(
                DatasetModel,
                func.ts_rank_cd(
                    DatasetModel.search_vector,
                    func.websearch_to_tsquery("english", query),
                    32,  # 32 normalizes all results between 0-1
                ).label("rank"),
            )
            .options(*load_options)
            .where(
                DatasetModel.search_vector.op("@@")(
                    func.websearch_to_tsquery("english", query)
                )
            )
            .order_by(desc("rank"))
        )
        results = self.db.execute(stmt).unique().all()
        filtered_datasets: list[DatasetsSearch] = []
        for row in results:
            if len(filtered_datasets) >= limit:
                return filtered_datasets
            dataset = row[0]
            rank = row[1]
            if self.is_visible_to_user(dataset, user):
                dataset.rank = rank
                filtered_datasets.append(dataset)
        return filtered_datasets

    def recalculate_search_vector_for(self, dataset_id: UUID) -> int:
        if settings.SEARCH_INDEXING_DISABLED:
            logger.debug("Search indexing is disabled, skipping recalculation")
            return 0
        sql = recalculate_search_vector_dataset_statement(dataset_id)
        result = self.db.execute(sql, {"dataset_id": dataset_id})
        return result.rowcount

    def recalculate_search_vector_datasets(self) -> int:
        if settings.SEARCH_INDEXING_DISABLED:
            logger.debug("Search indexing is disabled, skipping recalculation")
            return 0
        sql = recalculate_search_vector_datasets_statement()
        result = self.db.execute(sql)
        self.db.commit()
        return result.rowcount

    def get_datasets(
        self, user: UserModel, ids: Optional[Sequence[UUID]] = None
    ) -> Sequence[DatasetsGet]:
        load_options = get_dataset_load_options()
        default_lifecycle = self.db.scalar(
            select(DataProductLifeCycleModel).filter(
                DataProductLifeCycleModel.is_default
            )
        )
        query = (
            select(DatasetModel).options(*load_options).order_by(asc(DatasetModel.name))
        )
        if ids:
            query = query.where(DatasetModel.id.in_(ids))
        datasets = [
            dataset
            for dataset in self.db.scalars(query).unique().all()
            if self.is_visible_to_user(dataset, user)
        ]

        for dataset in datasets:
            if not dataset.lifecycle:
                dataset.lifecycle = default_lifecycle
        return datasets

    def get_datasets_for_embedding(self) -> Sequence[DatasetEmbed]:
        return [
            DatasetEmbed.model_validate(ds)
            for ds in (
                self.db.scalars(
                    select(DatasetModel)
                    .options(
                        selectinload(DatasetModel.data_product).raiseload("*"),
                        selectinload(DatasetModel.data_output_links)
                        .selectinload(DataOutputDatasetAssociationModel.data_output)
                        .raiseload("*"),
                    )
                    .order_by(asc(DatasetModel.name))
                )
                .unique()
                .all()
            )
        ]

    def get_user_datasets(self, user_id: UUID) -> Sequence[DatasetsGet]:
        return (
            self.db.scalars(
                select(DatasetModel)
                .options(
                    selectinload(DatasetModel.data_product_links).raiseload("*"),
                    selectinload(DatasetModel.data_output_links)
                    .selectinload(DataOutputDatasetAssociationModel.data_output)
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
        self.db.flush()
        self.recalculate_search_vector_for(model.id)
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
        self.db.flush()
        self.recalculate_search_vector_for(id)
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

    def update_dataset_usage(
        self,
        id: UUID,
        usage: DatasetUsageUpdate,
    ) -> DatasetModel:
        current_dataset = ensure_dataset_exists(id, self.db)
        current_dataset.usage = usage.usage
        self.db.commit()
        return current_dataset

    def get_graph_data(self, id: UUID, level: int) -> Graph:
        dataset = self.db.get(
            DatasetModel,
            id,
            options=[
                selectinload(DatasetModel.data_product_links),
                selectinload(DatasetModel.data_output_links),
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

        # if no data outputs are linked yet, still show the owner data product
        if level >= 2 and not dataset.data_output_links:
            nodes.append(
                Node(
                    id=f"{dataset.data_product.id}_2",
                    data=NodeData(
                        id=f"{dataset.data_product.id}",
                        name=dataset.data_product.name,
                        icon_key=dataset.data_product.type.icon_key,
                    ),
                    type=NodeType.dataProductNode,
                )
            )
            edges.append(
                Edge(
                    id=f"{dataset.data_product.id}-{dataset.id}-2",
                    target=dataset.id,
                    source=f"{dataset.data_product.id}_2",
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
            dataset.access_type != OutputPortAccessType.PRIVATE
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
