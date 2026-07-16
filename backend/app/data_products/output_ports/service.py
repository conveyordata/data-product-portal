import copy
from typing import Iterable, Optional, Sequence
from uuid import UUID

from fastapi import HTTPException, status
from fastembed import TextEmbedding
from sqlalchemy import func, select
from sqlalchemy.orm import Session, joinedload, raiseload, selectinload, undefer
from sqlalchemy.sql.base import ExecutableOption

from app.abstract_data_product.graph_utils import (
    get_graph_data_from_abstract_data_product,
)
from app.abstract_data_product.input_ports.model import (
    InputPort,
)
from app.abstract_data_product.input_ports.model import (
    InputPort as InputPortModel,
)
from app.abstract_data_product.type import AbstractDataProductType
from app.access_durations.enums import AccessDurationType
from app.access_durations.model import AccessDuration as AccessDurationModel
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
)
from app.data_products.model import ensure_data_product_exists
from app.data_products.output_port_technical_assets_link.model import (
    DataOutputDatasetAssociation as DataOutputDatasetAssociationModel,
)
from app.data_products.output_ports.enums import OutputPortAccessType
from app.data_products.output_ports.model import OutputPort as OutputPortModel
from app.data_products.output_ports.model import ensure_output_port_exists
from app.data_products.output_ports.schema import DatasetEmbedModel, OutputPort
from app.data_products.output_ports.schema_request import (
    CreateOutputPortRequest,
    DatasetUpdate,
    OutputPortAboutUpdate,
    OutputPortStatusUpdate,
    OutputPortUsageUpdate,
)
from app.data_products.output_ports.schema_response import (
    GetOutputPortAccessDurationsResponse,
    OutputPortAccessDuration,
)
from app.data_products.status import AbstractDataProductStatus
from app.data_products.technical_assets.model import (
    TechnicalAsset as TechnicalAssetModel,
)
from app.graph.edge import Edge
from app.graph.graph import Graph
from app.graph.node import Node, NodeData, NodeType
from app.resource_names.service import ResourceNameValidityType
from app.users.model import User as UserModel
from app.users.schema import User


def get_dataset_load_options() -> Sequence[ExecutableOption]:
    return [
        selectinload(OutputPortModel.data_product_links)
        .selectinload(InputPortModel.consuming_abstract_data_product)
        .raiseload("*"),
        selectinload(OutputPortModel.data_output_links)
        .selectinload(DataOutputDatasetAssociationModel.data_output)
        .options(
            joinedload(TechnicalAssetModel.configuration),
            joinedload(TechnicalAssetModel.owner),
            raiseload("*"),
        ),
    ]


class OutputPortService:
    def __init__(self, db: Session):
        self.db = db
        self.namespace_validator = NamespaceValidator(OutputPortModel)
        self.embedding_model = TextEmbedding(EMBEDDING_MODEL)

    def _ensure_data_product_not_deleting(self, data_product_id: UUID) -> None:
        dp = ensure_data_product_exists(data_product_id, self.db)
        if dp.status == AbstractDataProductStatus.DELETING:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Data product '{dp.name}' is pending deletion and cannot be modified",
            )

    def get_dataset(
        self, id: UUID, data_product_id: Optional[UUID] = None
    ) -> OutputPortModel:
        """DB fetch with all required eager loads, lifecycle defaulting, and tag roll-up.

        Does not enforce any visibility policy — callers decide whether to gate on user.
        """
        query = select(OutputPortModel).where(OutputPortModel.id == id)

        if data_product_id is not None:
            query = query.where(OutputPortModel.data_product_id == data_product_id)

        output_port = self.db.scalar(
            query.options(
                selectinload(OutputPortModel.data_output_links),
                selectinload(OutputPortModel.data_product_settings),
            )
        )

        if not output_port:
            raise self.not_found_exception(id)

        rolled_up_tags = set()
        for output_link in output_port.data_output_links:
            rolled_up_tags.update(output_link.data_output.tags)

        output_port.rolled_up_tags = rolled_up_tags

        if not output_port.lifecycle:
            default_lifecycle = self.db.scalar(
                select(DataProductLifeCycleModel).where(
                    DataProductLifeCycleModel.is_default
                )
            )
            output_port.lifecycle = default_lifecycle
        output_port.domain = output_port.data_product.domain
        return output_port

    def get_access_durations(
        self, id: UUID, user: UserModel, data_product_id: Optional[UUID] = None
    ) -> GetOutputPortAccessDurationsResponse:

        dataset = self.get_visible_output_port(id, user, data_product_id)

        time_bound_days: dict[AbstractDataProductType, int] = {
            row.abstract_data_product_type: row.days
            for row in self.db.scalars(
                select(AccessDurationModel).where(
                    AccessDurationModel.access_duration_type
                    == AccessDurationType.TIME_BOUND
                )
            ).all()
        }

        return GetOutputPortAccessDurationsResponse(
            id=dataset.id,
            data_product_access_duration=self._make_access_duration(
                dataset.data_product_access_duration_type,
                AbstractDataProductType.DATA_PRODUCT,
                time_bound_days,
            ),
            exploration_access_duration=self._make_access_duration(
                dataset.exploration_access_duration_type,
                AbstractDataProductType.EXPLORATION,
                time_bound_days,
            ),
        )

    @staticmethod
    def _make_access_duration(
        duration_type: AccessDurationType,
        product_type: AbstractDataProductType,
        time_bound_days: dict[AbstractDataProductType, int],
    ) -> OutputPortAccessDuration:
        return OutputPortAccessDuration(
            access_duration_type=duration_type,
            days=-1
            if duration_type == AccessDurationType.PERMANENT
            else time_bound_days.get(product_type, -1),
        )

    def get_visible_output_port(
        self, id: UUID, user: UserModel, data_product_id: Optional[UUID] = None
    ) -> OutputPortModel:
        """Fetch a dataset, raising 403 if the user cannot see it as a consumer.

        Use this for endpoints where dataset visibility must be enforced.

        For system/internal callers already authorised at the endpoint level, use
        get_dataset() instead.
        """
        dataset = self.get_dataset(id, data_product_id)
        if not self.is_visible_to_user(dataset, user):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have access to this private dataset",
            )
        return dataset

    def search_output_ports(
        self,
        query: Optional[str],
        limit: int,
        user: UserModel,
        current_user_assigned: bool,
    ) -> Sequence[OutputPortModel]:
        """An attempt was made to use the elbow method to determine a cut-off for returned results.
        The results of this method were quite poor, hence the search currently works as a sorting operation only,
        no filtering is applied other than the limit.
        """
        ordered_by = OutputPortModel.name.asc()
        if query:
            query_embedding = self.embedding_model.embed(query)
            semantic_score = (
                1 - OutputPortModel.embeddings.cosine_distance(*query_embedding)
            ).label("semantic_score")
            ts_query = func.websearch_to_tsquery("english", query)
            keyword_score = func.coalesce(
                func.ts_rank_cd(OutputPortModel.search_vector, ts_query, 32), 0
            ).label("keyword_score")

            semantic_weight = 2.0 / 3.0
            keyword_weight = 1.0 - semantic_weight
            ordered_by = (
                ((semantic_weight * semantic_score) + (keyword_weight * keyword_score))
                .label("hybrid_score")
                .desc()
            )

        stmt = (
            select(OutputPortModel)
            .order_by(ordered_by)
            # We currently apply a limit times 2, the reason is that without a limit the query is really slow, however we might miss results because of that
            .limit(limit * 2)
        )
        if current_user_assigned:
            stmt = stmt.where(OutputPortModel.assignments.any(user_id=user.id))
        stmt = stmt.options(
            undefer(OutputPortModel.abstract_data_product_count),
            undefer(OutputPortModel.technical_assets_count),
        )
        results = self.db.scalars(stmt).unique().all()

        visible_candidates: list[OutputPortModel] = []
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
            selectinload(OutputPortModel.data_product),
            selectinload(OutputPortModel.data_output_links).selectinload(
                DataOutputDatasetAssociationModel.data_output
            ),
        ]

    def recalculate_search_for_output_ports_of_product(
        self, data_product_id: UUID
    ) -> None:
        self.db.flush()
        datasets = (
            self.db.scalars(
                select(OutputPortModel)
                .where(OutputPortModel.data_product_id == data_product_id)
                .options(*self.recalculate_embeddings_load_options()),
            )
            .unique()
            .all()
        )
        self._recalculate_embeddings_and_search_vector(datasets)

    def recalculate_search(self, dataset_id: UUID) -> None:
        dataset = self.db.scalar(
            select(OutputPortModel)
            .where(OutputPortModel.id == dataset_id)
            .options(*self.recalculate_embeddings_load_options())
        )
        self._recalculate_embeddings_and_search_vector([dataset])

    def _recalculate_embeddings_and_search_vector(
        self, datasets: Sequence[OutputPortModel]
    ) -> None:
        embeddings = self.embedding_model.embed(
            DatasetEmbedModel.model_validate(ds).model_dump_json() for ds in datasets
        )
        for dataset, emb in zip(datasets, embeddings):
            dataset.embeddings = emb.tolist()
            self._recalculate_search_vector(dataset)
            self.db.add(dataset)

    @staticmethod
    def _recalculate_search_vector(output_port: OutputPortModel) -> None:
        output_port.search_vector = func.setweight(
            func.to_tsvector("english", output_port.name), "A"
        ).op("||")(
            func.setweight(func.to_tsvector("english", output_port.description), "B")
        )

    def recalculate_search_for_all_output_ports(self, batch_size: int = 50) -> None:
        dataset_ids = self.db.scalars(select(OutputPortModel.id)).all()

        # Process in batches to reduce load
        for i in range(0, len(dataset_ids), batch_size):
            batch_ids = dataset_ids[i : i + batch_size]

            batch_datasets = (
                self.db.scalars(
                    select(OutputPortModel)
                    .where(OutputPortModel.id.in_(batch_ids))
                    .options(*self.recalculate_embeddings_load_options())
                )
                .unique()
                .all()
            )

            if batch_datasets:
                self._recalculate_embeddings_and_search_vector(batch_datasets)
                self.db.flush()
        self.db.commit()

    def _fetch_tags(self, tag_ids: Iterable[UUID] = ()) -> list[TagModel]:
        tags = []
        for tag_id in tag_ids:
            tag = ensure_tag_exists(tag_id, self.db)
            tags.append(tag)

        return tags

    def create_output_port(
        self, data_product_id: UUID, dataset: CreateOutputPortRequest
    ) -> OutputPortModel:
        self._ensure_data_product_not_deleting(data_product_id)
        if (
            validity := self.namespace_validator.validate_namespace(
                dataset.namespace, self.db
            ).validity
        ) != ResourceNameValidityType.VALID:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid namespace: {validity.value}",
            )

        dataset_schema = dataset.parse_pydantic_schema()
        dataset_schema["data_product_id"] = data_product_id
        tags = self._fetch_tags(dataset_schema.pop("tag_ids", []))
        _ = dataset_schema.pop("owners", [])
        model = OutputPortModel(**dataset_schema, tags=tags)

        self.db.add(model)
        self.db.flush()
        self.recalculate_search(model.id)
        return model

    def remove_dataset(self, id: UUID, data_product_id: UUID) -> OutputPortModel:
        self._ensure_data_product_not_deleting(data_product_id)
        dataset = ensure_output_port_exists(
            id, self.db, data_product_id=data_product_id
        )
        if not dataset:
            raise self.not_found_exception(id)

        result = copy.deepcopy(dataset)
        self.db.delete(dataset)
        self.db.commit()
        return result

    def update_dataset(
        self, id: UUID, data_product_id: UUID, dataset: DatasetUpdate
    ) -> UUID:
        self._ensure_data_product_not_deleting(data_product_id)
        current_dataset = ensure_output_port_exists(
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
            != ResourceNameValidityType.VALID
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

    def update_output_port_about(
        self,
        id: UUID,
        data_product_id: UUID,
        output_port: OutputPortAboutUpdate,
    ) -> None:
        self._ensure_data_product_not_deleting(data_product_id)
        current_dataset = ensure_output_port_exists(
            id, self.db, data_product_id=data_product_id
        )
        current_dataset.about = output_port.about
        self.db.commit()

    def update_dataset_status(
        self,
        id: UUID,
        data_product_id: UUID,
        output_port: OutputPortStatusUpdate,
    ) -> None:
        self._ensure_data_product_not_deleting(data_product_id)
        current_output_port = ensure_output_port_exists(
            id, self.db, data_product_id=data_product_id
        )
        current_output_port.status = output_port.status
        self.db.commit()

    def update_dataset_usage(
        self,
        id: UUID,
        usage: OutputPortUsageUpdate,
    ) -> OutputPortModel:
        current_dataset = ensure_output_port_exists(id, self.db)
        self._ensure_data_product_not_deleting(current_dataset.data_product_id)
        current_dataset.usage = usage.usage
        self.db.commit()
        return current_dataset

    def get_graph_data(self, id: UUID, data_product_id: UUID, level: int) -> Graph:
        output_port: OutputPortModel | None = self.db.scalar(
            select(OutputPortModel)
            .where(OutputPortModel.id == id)
            .where(OutputPortModel.data_product_id == data_product_id)
            .options(
                selectinload(OutputPortModel.data_product_links),
                selectinload(OutputPortModel.data_output_links),
            )
        )
        if not output_port:
            raise self.not_found_exception(id)
        nodes = [
            Node(
                id=id,
                isMain=True,
                data=NodeData(
                    id=id,
                    name=output_port.name,
                    link_to_id=output_port.data_product_id,
                ),
                type=NodeType.outputPortNode,
            )
        ]
        edges = []
        for downstream_products in output_port.data_product_links:
            nodes.append(
                get_graph_data_from_abstract_data_product(
                    str(downstream_products.consuming_abstract_data_product_id),
                    downstream_products.consuming_abstract_data_product,
                )
            )
            edges.append(
                Edge(
                    id=f"{downstream_products.id}-{output_port.id}",
                    target=downstream_products.consuming_abstract_data_product_id,
                    source=output_port.id,
                    animated=downstream_products.status == DecisionStatus.APPROVED,
                )
            )

        for data_output_link in output_port.data_output_links:
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
                    type=NodeType.technicalAssetNode,
                )
            )
            edges.append(
                Edge(
                    id=f"{data_output.id}-{output_port.id}",
                    source=data_output.id,
                    target=output_port.id,
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
        if level >= 2 and not output_port.data_output_links:
            nodes.append(
                Node(
                    id=f"{output_port.data_product.id}_2",
                    data=NodeData(
                        id=f"{output_port.data_product.id}",
                        name=output_port.data_product.name,
                        icon_key=output_port.data_product.type.icon_key,
                    ),
                    type=NodeType.dataProductNode,
                )
            )
            edges.append(
                Edge(
                    id=f"{output_port.data_product.id}-{output_port.id}-2",
                    target=output_port.id,
                    source=f"{output_port.data_product.id}_2",
                    animated=True,
                )
            )

        return Graph(nodes=set(nodes), edges=set(edges))

    def is_visible_to_user(self, output_port: OutputPortModel, user: UserModel) -> bool:
        if (
            output_port.access_type != OutputPortAccessType.PRIVATE
            or Authorization().has_admin_role(user_id=str(user.id))
            or DatasetRoleAssignmentService(self.db).has_assignment(
                dataset_id=output_port.id, user=user
            )
        ):
            return True
        output_port = self.db.scalar(
            select(OutputPortModel)
            .where(OutputPortModel.id == output_port.id)
            .options(selectinload(OutputPortModel.data_product_links))
        )

        consuming_data_products = {
            link.consuming_abstract_data_product
            for link in output_port.data_product_links
            if link.status == DecisionStatus.APPROVED
        }

        user_data_products = {
            assignment.data_product
            for assignment in user.data_product_roles
            if assignment.decision == DecisionStatus.APPROVED
        }

        return bool(consuming_data_products & user_data_products)

    def get_output_ports(
        self, data_product_id: Optional[UUID], user: User
    ) -> Sequence[OutputPort]:
        query = select(OutputPortModel)
        if data_product_id is not None:
            ensure_data_product_exists(data_product_id, self.db)
            query = query.filter(OutputPortModel.data_product_id == data_product_id)

        results = self.db.scalars(query).unique().all()
        visible_candidates: list[OutputPortModel] = []
        for dataset in results:
            if self.is_visible_to_user(dataset, user):
                dataset.domain = dataset.data_product.domain
                visible_candidates.append(dataset)

        return visible_candidates

    def get_consuming_data_products(
        self, output_port_id: UUID, data_product_id: UUID
    ) -> Sequence[InputPort]:
        output_port = self.db.scalar(
            select(OutputPortModel)
            .where(OutputPortModel.id == output_port_id)
            .where(OutputPortModel.data_product_id == data_product_id)
            .options(
                selectinload(OutputPortModel.data_product_links).selectinload(
                    InputPortModel.consuming_abstract_data_product
                ),
                selectinload(OutputPortModel.data_product_links).selectinload(
                    InputPortModel.requests
                ),
            )
        )
        if not output_port:
            raise self.not_found_exception(output_port_id)
        return output_port.data_product_links

    def not_found_exception(self, output_port_id: UUID) -> HTTPException:
        return HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Output port {output_port_id} not found",
        )
