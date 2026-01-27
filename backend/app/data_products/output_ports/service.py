import copy
from typing import Iterable, Optional, Sequence
from uuid import UUID

from fastapi import HTTPException, status
from fastembed import TextEmbedding
from sqlalchemy import asc, func, select
from sqlalchemy.orm import Session, joinedload, raiseload, selectinload
from sqlalchemy.sql.base import ExecutableOption

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
from app.core.embed.model import EMBEDDING_MODEL
from app.core.namespace.validation import (
    NamespaceValidator,
    NamespaceValidityType,
)
from app.data_products.model import ensure_data_product_exists
from app.data_products.output_port_technical_assets_link.model import (
    DataOutputDatasetAssociation as DataOutputDatasetAssociationModel,
)
from app.data_products.output_ports.enums import OutputPortAccessType
from app.data_products.output_ports.input_ports.model import (
    DataProductDatasetAssociation as DataProductDatasetAssociationModel,
)
from app.data_products.output_ports.model import Dataset as DatasetModel
from app.data_products.output_ports.model import ensure_dataset_exists
from app.data_products.output_ports.schema import DatasetEmbedModel, OutputPort
from app.data_products.output_ports.schema_request import (
    CreateOutputPortRequest,
    DatasetAboutUpdate,
    DatasetStatusUpdate,
    DatasetUpdate,
    DatasetUsageUpdate,
)
from app.data_products.output_ports.schema_response import (
    DatasetGet,
    DatasetsGet,
)
from app.data_products.technical_assets.model import DataOutput
from app.graph.edge import Edge
from app.graph.graph import Graph
from app.graph.node import Node, NodeData, NodeType
from app.search_output_ports.schema_response import SearchDatasets
from app.users.model import User as UserModel
from app.users.schema import User


def get_dataset_load_options() -> Sequence[ExecutableOption]:
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


class OutputPortService:
    def __init__(self, db: Session):
        self.db = db
        self.namespace_validator = NamespaceValidator(DatasetModel)
        self.embedding_model = TextEmbedding(EMBEDDING_MODEL)

    def get_dataset(
        self, id: UUID, user: UserModel, data_product_id: Optional[UUID] = None
    ) -> DatasetGet:
        query = select(DatasetModel).where(DatasetModel.id == id)

        if data_product_id is not None:
            query = query.where(DatasetModel.data_product_id == data_product_id)

        dataset = self.db.scalar(
            query.options(
                selectinload(DatasetModel.data_product_links),
                selectinload(DatasetModel.data_output_links),
            )
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
        dataset.domain = dataset.data_product.domain
        return dataset

    def search_datasets(
        self, query: str, limit: int, user: UserModel
    ) -> Sequence[SearchDatasets]:
        """An attempt was made to use the elbow method to determine a cut-off for returned results.
        The results of this method were quite poor, hence the search currently works as a sorting operation only,
        no filtering is applied other than the limit.
        """
        query_embedding = self.embedding_model.embed(query)
        semantic_score = (
            1 - DatasetModel.embeddings.cosine_distance(*query_embedding)
        ).label("semantic_score")
        ts_query = func.websearch_to_tsquery("english", query)
        keyword_score = func.coalesce(
            func.ts_rank_cd(DatasetModel.search_vector, ts_query, 32), 0
        ).label("keyword_score")

        semantic_weight = 2.0 / 3.0
        keyword_weight = 1.0 - semantic_weight
        hybrid_score = (
            (semantic_weight * semantic_score) + (keyword_weight * keyword_score)
        ).label("hybrid_score")

        stmt = (
            select(DatasetModel)
            .options(*get_dataset_load_options())
            .order_by(hybrid_score.desc())
            # We currently apply a limit times 2, the reason is that without a limit the query is really slow, however we might miss results because of that
            .limit(limit * 2)
        )
        results = self.db.scalars(stmt).unique().all()

        visible_candidates: list[DatasetModel] = []
        for dataset in results:
            if self.is_visible_to_user(dataset, user):
                dataset.domain = dataset.data_product.domain
                visible_candidates.append(dataset)

                if len(visible_candidates) >= limit:
                    return visible_candidates

        return visible_candidates

    @staticmethod
    def recalculate_embeddings_load_options():
        return [
            selectinload(DatasetModel.data_product),
            selectinload(DatasetModel.data_output_links).selectinload(
                DataOutputDatasetAssociationModel.data_output
            ),
        ]

    def recalculate_search_for_output_ports_of_product(
        self, data_product_id: UUID
    ) -> None:
        self.db.flush()
        datasets = (
            self.db.scalars(
                select(DatasetModel)
                .where(DatasetModel.data_product_id == data_product_id)
                .options(*self.recalculate_embeddings_load_options()),
            )
            .unique()
            .all()
        )
        self._recalculate_embeddings_and_search_vector(datasets)

    def recalculate_search(self, dataset_id: UUID) -> None:
        dataset = self.db.scalar(
            select(DatasetModel)
            .where(DatasetModel.id == dataset_id)
            .options(*self.recalculate_embeddings_load_options())
        )
        self._recalculate_embeddings_and_search_vector([dataset])

    def _recalculate_embeddings_and_search_vector(
        self, datasets: Sequence[DatasetModel]
    ) -> None:
        embeddings = self.embedding_model.embed(
            DatasetEmbedModel.model_validate(ds).model_dump_json() for ds in datasets
        )
        for dataset, emb in zip(datasets, embeddings):
            dataset.embeddings = emb.tolist()
            self._recalculate_search_vector(dataset)
            self.db.add(dataset)

    @staticmethod
    def _recalculate_search_vector(dataset: DatasetModel) -> None:
        dataset.search_vector = func.setweight(
            func.to_tsvector("english", dataset.name), "A"
        ).op("||")(
            func.setweight(func.to_tsvector("english", dataset.description), "B")
        )

    def recalculate_search_for_all_output_ports(self, batch_size: int = 50) -> None:
        dataset_ids = self.db.scalars(select(DatasetModel.id)).all()

        # Process in batches to reduce load
        for i in range(0, len(dataset_ids), batch_size):
            batch_ids = dataset_ids[i : i + batch_size]

            batch_datasets = (
                self.db.scalars(
                    select(DatasetModel)
                    .where(DatasetModel.id.in_(batch_ids))
                    .options(*self.recalculate_embeddings_load_options())
                )
                .unique()
                .all()
            )

            if batch_datasets:
                self._recalculate_embeddings_and_search_vector(batch_datasets)
                self.db.flush()
        self.db.commit()

    def get_datasets(
        self, user: UserModel, check_user_assigned: bool = False
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
        if check_user_assigned:
            query = query.filter(DatasetModel.assignments.any(user_id=user.id))
        datasets = [
            dataset
            for dataset in self.db.scalars(query).unique().all()
            if self.is_visible_to_user(dataset, user)
        ]

        for dataset in datasets:
            if not dataset.lifecycle:
                dataset.lifecycle = default_lifecycle
            dataset.domain = dataset.data_product.domain
        return datasets

    def _fetch_tags(self, tag_ids: Iterable[UUID] = ()) -> list[TagModel]:
        tags = []
        for tag_id in tag_ids:
            tag = ensure_tag_exists(tag_id, self.db)
            tags.append(tag)

        return tags

    def create_dataset(
        self, data_product_id: UUID, dataset: CreateOutputPortRequest
    ) -> DatasetModel:
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
        dataset_schema["data_product_id"] = data_product_id
        tags = self._fetch_tags(dataset_schema.pop("tag_ids", []))
        _ = dataset_schema.pop("owners", [])
        model = DatasetModel(**dataset_schema, tags=tags)

        self.db.add(model)
        self.db.flush()
        self.recalculate_search(model.id)
        self.db.commit()
        return model

    def remove_dataset(self, id: UUID, data_product_id: UUID) -> DatasetModel:
        dataset = ensure_dataset_exists(id, self.db, data_product_id=data_product_id)
        if not dataset:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=f"Dataset {id} not found"
            )

        result = copy.deepcopy(dataset)
        self.db.delete(dataset)
        self.db.commit()
        return result

    def update_dataset(
        self, id: UUID, data_product_id: UUID, dataset: DatasetUpdate
    ) -> UUID:
        current_dataset = ensure_dataset_exists(
            id, self.db, data_product_id=data_product_id
        )
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
        self.recalculate_search(id)
        self.db.commit()
        return current_dataset.id

    def update_dataset_about(
        self,
        id: UUID,
        data_product_id: UUID,
        dataset: DatasetAboutUpdate,
    ) -> None:
        current_dataset = ensure_dataset_exists(
            id, self.db, data_product_id=data_product_id
        )
        current_dataset.about = dataset.about
        self.db.commit()

    def update_dataset_status(
        self,
        id: UUID,
        data_product_id: UUID,
        dataset: DatasetStatusUpdate,
    ) -> None:
        current_dataset = ensure_dataset_exists(
            id, self.db, data_product_id=data_product_id
        )
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

    def get_graph_data(self, id: UUID, data_product_id: UUID, level: int) -> Graph:
        dataset = self.db.scalar(
            select(DatasetModel)
            .where(DatasetModel.id == id)
            .where(DatasetModel.data_product_id == data_product_id)
            .options(
                selectinload(DatasetModel.data_product_links),
                selectinload(DatasetModel.data_output_links),
            )
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

    def get_output_ports(self, data_product_id: Optional[UUID]) -> Sequence[OutputPort]:
        query = select(DatasetModel)
        if data_product_id is not None:
            ensure_data_product_exists(data_product_id, self.db)
            query = query.filter(DatasetModel.data_product_id == data_product_id)
        return self.db.scalars(query).unique().all()
