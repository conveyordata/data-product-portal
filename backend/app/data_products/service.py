import copy
from typing import Optional, Sequence, assert_never
from uuid import UUID
from warnings import deprecated

from fastapi import HTTPException, status
from fastembed import TextEmbedding
from sqlalchemy import asc, distinct, func, select
from sqlalchemy.orm import joinedload, selectinload, undefer, with_expression
from sqlalchemy.orm.util import identity_key

from app.abstract_data_product.graph_utils import (
    get_graph_data_from_abstract_data_product,
)
from app.abstract_data_product.input_ports.enums import InputPortStatus
from app.abstract_data_product.input_ports.model import (
    InputPort as InputPortModel,
)
from app.abstract_data_product.service import AbstractDataProductService
from app.authorization.role_assignments.enums import AssignmentFilter, DecisionStatus
from app.authorization.roles.schema import Prototype
from app.configuration.data_product_lifecycles.model import (
    DataProductLifecycle as DataProductLifeCycleModel,
)
from app.configuration.data_product_settings.model import DataProductSettingValue
from app.configuration.domains.service import DomainService
from app.configuration.environments.model import Environment as EnvironmentModel
from app.configuration.tags.model import Tag as TagModel
from app.configuration.tags.model import ensure_tag_exists
from app.configuration.tags.schema import Tag
from app.core import context
from app.core.authz import CasbinPolicies
from app.core.authz.rules import DATA_PRODUCT_READER_ROLE, EVERYONE
from app.core.aws.get_url import _get_data_product_role_arn
from app.core.context import discard_events
from app.core.embed.model import get_text_embedding_model
from app.core.webhooks.events import DataProductEnvironmentAddedEvent
from app.data_products.model import DataProduct as DataProductModel
from app.data_products.model import (
    DataProductEnvironment,
    DataProductVisibility,
    ensure_data_product_exists,
)
from app.data_products.output_port_technical_assets_link.model import (
    TechnicalAssetOutputPortAssociation,
)
from app.data_products.output_ports.model import OutputPort as OutputPortModel
from app.data_products.schema import DataProductEmbedModel
from app.data_products.schema_request import (
    DataProductAboutUpdate,
    DataProductCreate,
    DataProductStatusUpdate,
    DataProductUpdate,
    DataProductUsageUpdate,
)
from app.data_products.schema_response import (
    GetDataProductResponse,
    UpdateDataProductResponse,
)
from app.data_products.technical_assets.environment_configuration_service import (
    TechnicalAssetEnvironmentConfigurationService,
)
from app.data_products.technical_assets.model import (
    TechnicalAsset as TechnicalAssetModel,
)
from app.database.database import SKIP_OUTPUT_PORT_ACCESS_FUNCTION_FILTER, UNFILTERED
from app.database.visibility import member_of, output_port_visible_ignoring_consumption
from app.graph.edge import Edge
from app.graph.graph import Graph
from app.graph.node import Node, NodeData, NodeType
from app.resource_names.service import ResourceNameService, ResourceNameValidityType
from app.users.model import User as UserModel
from app.users.schema import User


class DataProductService(AbstractDataProductService):
    @property
    def embedding_model(self) -> TextEmbedding:
        return get_text_embedding_model()

    @staticmethod
    def _sync_public_reader_grouping(
        data_product_id: UUID, visibility: DataProductVisibility
    ) -> None:
        match visibility:
            case DataProductVisibility.DISCOVERABLE:
                CasbinPolicies().assign_resource_role(
                    user_id=EVERYONE,
                    role_id=DATA_PRODUCT_READER_ROLE,
                    resource_id=str(data_product_id),
                )
            case DataProductVisibility.HIDDEN:
                CasbinPolicies().revoke_resource_role(
                    user_id=EVERYONE,
                    role_id=DATA_PRODUCT_READER_ROLE,
                    resource_id=str(data_product_id),
                )
            case _:
                assert_never(visibility)

    def get_data_product_settings(
        self, data_product_id: UUID
    ) -> Sequence[DataProductSettingValue]:
        ensure_data_product_exists(data_product_id, self.db)
        return self.db.scalars(
            select(DataProductSettingValue).where(
                DataProductSettingValue.data_product_id == data_product_id
            )
        ).all()

    def get_rolled_up_tags(self, data_product_id: UUID) -> set[Tag]:
        ensure_data_product_exists(data_product_id, self.db)
        rolled_up_tags = set()

        output_port_tags = self.db.scalars(
            select(TagModel)
            .join(OutputPortModel.tags)
            .where(OutputPortModel.data_product_id == data_product_id)
        ).all()
        rolled_up_tags.update(output_port_tags)

        technical_asset_tags = self.db.scalars(
            select(TagModel)
            .join(TechnicalAssetModel.tags)
            .where(TechnicalAssetModel.owner_id == data_product_id)
        ).all()
        rolled_up_tags.update(technical_asset_tags)

        return rolled_up_tags

    def get_data_product(self, id: UUID) -> GetDataProductResponse:
        # db.scalar instead of db.get: db.get uses the identity map and may return a
        # cached object without tags loaded, silently ignoring the selectinload option.
        data_product = self.db.scalar(
            select(DataProductModel)
            .where(DataProductModel.id == id)
            .options(
                selectinload(DataProductModel.tags),
                selectinload(DataProductModel.environments),
            )
        )
        default_lifecycle = self.db.scalar(
            select(DataProductLifeCycleModel).filter(
                DataProductLifeCycleModel.is_default
            )
        )
        if not data_product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Data Product not found"
            )

        if not data_product.lifecycle:
            data_product.lifecycle = default_lifecycle
        return data_product

    def get_data_products(
        self,
        *,
        assignment_filter: AssignmentFilter,
    ) -> Sequence[DataProductModel]:
        query = select(DataProductModel).options(
            selectinload(DataProductModel.tags).raiseload("*"),
            selectinload(DataProductModel.environments),
            undefer(DataProductModel.input_port_count),
        )
        match assignment_filter:
            case AssignmentFilter.ALL:
                pass
            case AssignmentFilter.ONLY_ASSIGNED:
                query = query.where(member_of(self.db, DataProductModel.id))
            case _:
                assert_never(assignment_filter)
        query = query.order_by(asc(DataProductModel.name))
        return self._with_default_lifecycle(self.db.scalars(query).unique().all())

    def search_data_products(
        self, query: Optional[str], limit: int
    ) -> Sequence[DataProductModel]:
        ordered_by = DataProductModel.name.asc()
        if query:
            query_embedding = self.embedding_model.embed(query)
            ordered_by = DataProductModel.embeddings.cosine_distance(
                *query_embedding
            ).asc()

        # Leave out private Output Ports the user only sees
        # because one of their Data Products consumes them: the marketplace lists
        # what a user can request, not what they already use.
        visible_output_port = output_port_visible_ignoring_consumption(
            self.db, OutputPortModel
        )
        stmt = (
            select(DataProductModel)
            .options(
                selectinload(DataProductModel.tags).raiseload("*"),
                selectinload(DataProductModel.datasets.and_(visible_output_port)),
                with_expression(
                    DataProductModel.consumer_count,
                    self._consumer_count(visible_output_port),
                ),
            )
            .order_by(ordered_by)
            .limit(limit)
            .execution_options(**{SKIP_OUTPUT_PORT_ACCESS_FUNCTION_FILTER: True})
        )
        return self._with_default_lifecycle(self.db.scalars(stmt).unique().all())

    @staticmethod
    def _consumer_count(visible_output_port):
        return (
            select(
                func.count(distinct(InputPortModel.consuming_abstract_data_product_id))
            )
            .join(OutputPortModel, OutputPortModel.id == InputPortModel.output_port_id)
            .where(
                OutputPortModel.data_product_id == DataProductModel.id,
                InputPortModel.status == InputPortStatus.APPROVED,
                visible_output_port,
            )
            .scalar_subquery()
        )

    def _with_default_lifecycle(
        self, dps: Sequence[DataProductModel]
    ) -> Sequence[DataProductModel]:
        default_lifecycle = self.db.scalar(
            select(DataProductLifeCycleModel).filter(
                DataProductLifeCycleModel.is_default
            )
        )
        for dp in dps:
            if not dp.lifecycle:
                dp.lifecycle = default_lifecycle
        return dps

    def get_owners(self, id: UUID) -> Sequence[User]:
        data_product = ensure_data_product_exists(
            id,
            self.db,
            options=[selectinload(DataProductModel.assignments)],
            populate_existing=True,
        )
        identity_ids = [
            assignment.identity_id
            for assignment in data_product.assignments
            if assignment.role.prototype == Prototype.OWNER
        ]
        return self.db.scalars(
            select(UserModel).filter(UserModel.id.in_(identity_ids))
        ).all()

    def _get_tags(self, tag_ids: list[UUID]) -> list[TagModel]:
        return [ensure_tag_exists(tag_id, self.db) for tag_id in tag_ids]

    def create_data_product(
        self,
        data_product: DataProductCreate,
    ) -> DataProductModel:
        if (
            validity := ResourceNameService(model=DataProductModel)
            .validate_resource_name(data_product.namespace, self.db)
            .validity
        ) != ResourceNameValidityType.VALID:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid namespace: {validity.value}",
            )

        DomainService(self.db).ensure_assignable(data_product.domain_id)
        data_product_schema = data_product.model_dump(
            exclude={"input_ports", "environment_ids"}
        )
        tags = self._get_tags(data_product_schema.pop("tag_ids", []))
        _ = data_product_schema.pop("owners", [])
        model = DataProductModel(**data_product_schema, tags=tags, environments=[])
        self.db.add(model)
        self._set_environments(model, data_product.environment_ids)
        self._sync_public_reader_grouping(model.id, model.visibility)
        self.recalculate_search(model.id)
        return model

    def remove_data_product(self, id: UUID) -> DataProductModel:
        data_product = self.db.get(DataProductModel, id)
        if not data_product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Data Product {id} not found",
            )

        result = copy.deepcopy(data_product)
        output_port_ids = self.db.scalars(
            select(OutputPortModel.id).where(OutputPortModel.data_product_id == id),
            execution_options=UNFILTERED,
        ).all()
        self.db.delete(data_product)
        self.db.flush()
        policies = CasbinPolicies()
        for resource_id in (id, *output_port_ids):
            policies.clear_assignments_for_resource(resource_id=resource_id)
        return result

    def update_data_product(
        self,
        id: UUID,
        data_product: DataProductUpdate,
    ) -> UpdateDataProductResponse:
        current_data_product = self.db.scalar(
            select(DataProductModel)
            .where(DataProductModel.id == id)
            .with_for_update(of=DataProductModel)
            .execution_options(populate_existing=True)
            .options(
                selectinload(DataProductModel.tags),
                selectinload(DataProductModel.environments),
            )
        )
        if current_data_product is None:
            raise HTTPException(status_code=404, detail="Data Product not found")
        self._ensure_not_deleting(current_data_product)
        update_data_product = data_product.model_dump(
            exclude_unset=True, exclude={"environment_ids"}
        )
        if data_product.domain_id != current_data_product.domain_id:
            DomainService(self.db).ensure_assignable(data_product.domain_id)

        if (
            current_data_product.namespace != data_product.namespace
            and (
                validity := ResourceNameService(model=DataProductModel)
                .validate_resource_name(data_product.namespace, self.db)
                .validity
            )
            != ResourceNameValidityType.VALID
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid namespace: {validity.value}",
            )

        for k, v in update_data_product.items():
            if k == "tag_ids":
                new_tags = self._get_tags(v)
                current_data_product.tags = new_tags
            else:
                setattr(current_data_product, k, v) if v else None
        if data_product.environment_ids is not None:
            self._set_environments(current_data_product, data_product.environment_ids)
        self.db.flush()
        self.recalculate_search(current_data_product.id)
        return UpdateDataProductResponse(id=current_data_product.id)

    def _set_environments(
        self, data_product: DataProductModel, environment_ids: list[UUID] | None
    ) -> None:
        query = select(EnvironmentModel)
        if environment_ids is None:
            query = query.where(EnvironmentModel.is_global.is_(True))
        else:
            requested_ids = set(environment_ids)
            if len(environment_ids) != len(requested_ids):
                raise HTTPException(
                    status_code=400, detail="Duplicate environment ids provided"
                )
            query = query.where(EnvironmentModel.id.in_(requested_ids))

        environments = list(self.db.scalars(query).all())
        resolved_ids = {environment.id for environment in environments}
        if environment_ids is not None and resolved_ids != requested_ids:
            raise HTTPException(
                status_code=400, detail="Invalid environment ids provided"
            )
        if not environments:
            raise HTTPException(
                status_code=400,
                detail="Select at least one environment for the Data Product",
            )

        existing_ids = {item.environment_id for item in data_product.environments}
        if not existing_ids.issubset(resolved_ids):
            raise HTTPException(
                status_code=400,
                detail="Environments cannot be removed from a Data Product",
            )
        additions = [
            DataProductEnvironment(
                environment=environment, environment_id=environment.id
            )
            for environment in environments
            if environment.id not in existing_ids
        ]
        data_product.environments.extend(additions)
        self.db.flush()
        TechnicalAssetEnvironmentConfigurationService(self.db).add_environments(
            data_product, [item.environment for item in additions]
        )
        context.queue_events(
            [
                DataProductEnvironmentAddedEvent(
                    data_product_id=data_product.id,
                    environment=item.environment.acronym,
                    creation_date=item.creation_date,
                )
                for item in additions
            ]
        )

    def update_data_product_about(
        self,
        id: UUID,
        data_product: DataProductAboutUpdate,
    ) -> DataProductModel:
        current_data_product = ensure_data_product_exists(id, self.db)
        self._ensure_not_deleting(current_data_product)
        current_data_product.about = data_product.about
        self.db.flush()
        self.recalculate_search(id)
        return current_data_product

    def update_data_product_status(
        self,
        id: UUID,
        data_product: DataProductStatusUpdate,
    ) -> DataProductModel:
        current_data_product = ensure_data_product_exists(id, self.db)
        self._ensure_not_deleting(current_data_product)
        current_data_product.status = data_product.status
        self.db.flush()
        return current_data_product

    def update_data_product_usage(
        self,
        id: UUID,
        usage: DataProductUsageUpdate,
    ) -> DataProductModel:
        current_data_product = ensure_data_product_exists(id, self.db)
        self._ensure_not_deleting(current_data_product)
        current_data_product.usage = usage.usage
        self.db.flush()
        return current_data_product

    @deprecated("Should use generate_signin_url instead")
    def get_data_product_role_arn(self, id: UUID, environment: str) -> str:
        return _get_data_product_role_arn(id, environment, self.db)

    def get_graph_data(self, id: UUID, level: int) -> Graph:
        product = self.db.get(
            DataProductModel,
            id,
            populate_existing=True,
            options=[selectinload(DataProductModel.datasets)],
        )
        nodes = [
            Node(
                id=id,
                isMain=True,
                data=NodeData(id=id, name=product.name, icon_key=product.type.icon_key),
                type=NodeType.dataProductNode,
            )
        ]
        edges = []

        input_ports = (
            self.db.scalars(
                select(InputPortModel).filter_by(consuming_abstract_data_product_id=id)
            )
            .unique()
            .all()
        )
        technical_assets = (
            self.db.scalars(
                select(TechnicalAssetModel)
                .options(
                    joinedload(TechnicalAssetModel.output_port_links)
                    .selectinload(TechnicalAssetOutputPortAssociation.output_port)
                    .selectinload(OutputPortModel.data_product_links)
                )
                .filter_by(owner_id=id)
                .execution_options(populate_existing=True)
            )
            .unique()
            .all()
        )

        for upstream_datasets in input_ports:
            # Skip private output ports with no access they show up as None
            if upstream_datasets.output_port is None:
                continue
            nodes.append(
                Node(
                    id=upstream_datasets.id,
                    data=NodeData(
                        id=upstream_datasets.output_port_id,
                        name=upstream_datasets.output_port.name,
                        link_to_id=upstream_datasets.output_port.data_product_id,
                    ),
                    type=NodeType.outputPortNode,
                )
            )
            edges.append(
                Edge(
                    id=f"{upstream_datasets.id}-{product.id}",
                    target=product.id,
                    source=upstream_datasets.id,
                    animated=upstream_datasets.status == DecisionStatus.APPROVED,
                )
            )

        for technical_asset in technical_assets:
            nodes.append(
                Node(
                    id=technical_asset.id,
                    data=NodeData(
                        id=technical_asset.id,
                        icon_key=technical_asset.configuration.configuration_type,
                        name=technical_asset.name,
                        link_to_id=technical_asset.owner_id,
                    ),
                    type=NodeType.technicalAssetNode,
                )
            )
            edges.append(
                Edge(
                    id=f"{technical_asset.id}-{product.id}",
                    source=product.id,
                    target=technical_asset.id,
                    animated=True,
                )
            )
            if level >= 2:
                for downstream_datasets in technical_asset.output_port_links:
                    nodes.append(
                        Node(
                            id=f"{downstream_datasets.output_port_id}_2",
                            data=NodeData(
                                id=f"{downstream_datasets.output_port_id}",
                                name=downstream_datasets.output_port.name,
                                link_to_id=downstream_datasets.output_port.data_product_id,
                            ),
                            type=NodeType.outputPortNode,
                        )
                    )
                    edges.append(
                        Edge(
                            id=f"{downstream_datasets.output_port_id}-{technical_asset.id}-2",
                            target=f"{downstream_datasets.output_port_id}_2",
                            source=technical_asset.id,
                            animated=downstream_datasets.status
                            == DecisionStatus.APPROVED,
                        )
                    )
                    if level >= 3:
                        for (
                            downstream_dps
                        ) in downstream_datasets.output_port.data_product_links:
                            # A hidden data product will result in None, filter it out
                            if downstream_dps.consuming_abstract_data_product is None:
                                continue
                            node_id = f"{downstream_dps.id}_3"
                            nodes.append(
                                get_graph_data_from_abstract_data_product(
                                    node_id,
                                    downstream_dps.consuming_abstract_data_product,
                                )
                            )
                            edges.append(
                                Edge(
                                    id=(
                                        f"{downstream_dps.id}-"
                                        f"{downstream_datasets.output_port.id}-3"
                                    ),
                                    target=node_id,
                                    source=f"{downstream_datasets.output_port.id}_2",
                                    animated=downstream_dps.status
                                    == DecisionStatus.APPROVED,
                                )
                            )

        # if no data outputs are present, still show the children datasets
        if not technical_assets:
            for downstream_dataset in product.datasets:
                nodes.append(
                    Node(
                        id=downstream_dataset.id,
                        data=NodeData(
                            id=downstream_dataset.id,
                            name=downstream_dataset.name,
                            link_to_id=downstream_dataset.data_product_id,
                        ),
                        type=NodeType.outputPortNode,
                    )
                )
                edges.append(
                    Edge(
                        id=f"{product.id}-{downstream_dataset.id}-direct",
                        source=product.id,
                        target=downstream_dataset.id,
                        animated=True,
                    )
                )

        return Graph(nodes=set(nodes), edges=set(edges))

    def recalculate_search(self, id: UUID) -> None:
        self.db.flush()
        if cached := self.db.identity_map.get(identity_key(DataProductModel, id)):
            self.db.expire(cached, ["datasets", "technical_assets"])
        data_product = self.db.scalar(
            select(DataProductModel)
            .where(DataProductModel.id == id)
            .options(*self._recalculate_search_load_options()),
            # Recalculation will never be done by users, so we can safely skip the filters here
            execution_options=UNFILTERED,
        )
        self._recalculate_embeddings([data_product])

    def recalculate_search_for_all_data_products(self, batch_size: int = 50) -> None:
        data_product_ids = self.db.scalars(
            select(DataProductModel.id).execution_options(**UNFILTERED)
        ).all()
        for i in range(0, len(data_product_ids), batch_size):
            data_products = (
                self.db.scalars(
                    select(DataProductModel)
                    .where(
                        DataProductModel.id.in_(data_product_ids[i : i + batch_size])
                    )
                    .options(*self._recalculate_search_load_options())
                    .execution_options(**UNFILTERED),
                )
                .unique()
                .all()
            )
            if data_products:
                self._recalculate_embeddings(data_products)
        # Allow commit since this is a batch operation and we want to persist changes. Not used in routing
        self.db.commit()  # allow-commit

    @staticmethod
    def _recalculate_search_load_options():
        return [
            selectinload(DataProductModel.datasets),
            selectinload(DataProductModel.technical_assets).selectinload(
                TechnicalAssetModel.output_port_links
            ),
        ]

    def _recalculate_embeddings(
        self, data_products: Sequence[DataProductModel]
    ) -> None:
        # Flush pending domain changes first so their events are not discarded below
        self.db.flush()
        embeddings = self.embedding_model.embed(
            DataProductEmbedModel.model_validate(dp).model_dump_json()
            for dp in data_products
        )
        # Search index maintenance is not a domain change, so emit no webhook events
        with discard_events():
            for data_product, emb in zip(data_products, embeddings):
                data_product.embeddings = emb.tolist()
                self.db.add(data_product)
            self.db.flush()
