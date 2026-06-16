import copy
from typing import Optional, Sequence
from uuid import UUID
from warnings import deprecated

from fastapi import HTTPException, status
from sqlalchemy import asc, select
from sqlalchemy.orm import Session, joinedload, selectinload, undefer

from app.abstract_data_product.graph_utils import (
    get_graph_data_from_abstract_data_product,
)
from app.abstract_data_product.service import AbstractDataProductService
from app.authorization.role_assignments.enums import DecisionStatus
from app.authorization.roles.schema import Prototype
from app.configuration.data_product_lifecycles.model import (
    DataProductLifecycle as DataProductLifeCycleModel,
)
from app.configuration.data_product_settings.model import DataProductSettingValue
from app.configuration.tags.model import Tag as TagModel
from app.configuration.tags.model import ensure_tag_exists
from app.configuration.tags.schema import Tag
from app.core.aws.get_url import _get_data_product_role_arn
from app.core.context import queue_event
from app.core.namespace.validation import (
    NamespaceValidator,
    TechnicalAssetNamespaceValidator,
)
from app.core.webhooks.events import (
    DataProductCreatedEvent,
    DataProductDeletedEvent,
    DataProductUpdatedEvent,
)
from app.data_products.model import DataProduct as DataProductModel
from app.data_products.model import ensure_data_product_exists
from app.data_products.output_port_technical_assets_link.model import (
    DataOutputDatasetAssociation,
)
from app.data_products.output_ports.input_ports.model import (
    InputPort as InputPortModel,
)
from app.data_products.output_ports.model import Dataset as DatasetModel
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
from app.data_products.technical_assets.model import (
    TechnicalAsset as TechnicalAssetModel,
)
from app.graph.edge import Edge
from app.graph.graph import Graph
from app.graph.node import Node, NodeData, NodeType
from app.resource_names.service import ResourceNameService, ResourceNameValidityType
from app.users.model import User as UserModel
from app.users.schema import User


class DataProductService(AbstractDataProductService):
    def __init__(self, db: Session):
        super().__init__(db)
        self.namespace_validator = NamespaceValidator(DataProductModel)
        self.technical_asset_namespace_validator = TechnicalAssetNamespaceValidator()

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
            .join(DatasetModel.tags)
            .where(DatasetModel.data_product_id == data_product_id)
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
            .options(selectinload(DataProductModel.tags))
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
        filter_to_user_with_assigment: Optional[UUID] = None,
    ) -> Sequence[DataProductModel]:
        default_lifecycle = self.db.scalar(
            select(DataProductLifeCycleModel).filter(
                DataProductLifeCycleModel.is_default
            )
        )
        query = select(DataProductModel).options(
            selectinload(DataProductModel.tags).raiseload("*"),
            undefer(DataProductModel.input_port_count),
        )
        if filter_to_user_with_assigment:
            query = query.filter(
                DataProductModel.assignments.any(
                    user_id=filter_to_user_with_assigment,
                    decision=DecisionStatus.APPROVED,
                )
            )
        query = query.order_by(asc(DataProductModel.name))

        dps = self.db.scalars(query).unique().all()

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
        user_ids = [
            assignment.user_id
            for assignment in data_product.assignments
            if assignment.role.prototype == Prototype.OWNER
        ]
        return self.db.scalars(
            select(UserModel).filter(UserModel.id.in_(user_ids))
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

        data_product_schema = data_product.model_dump(exclude={"input_ports"})
        tags = self._get_tags(data_product_schema.pop("tag_ids", []))
        _ = data_product_schema.pop("owners", [])
        model = DataProductModel(**data_product_schema, tags=tags)
        self.db.add(model)
        self.db.commit()
        queue_event(DataProductCreatedEvent(after=model.to_event()))
        return model

    def remove_data_product(self, id: UUID) -> DataProductModel:
        data_product = self.db.get(DataProductModel, id)
        if not data_product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Data Product {id} not found",
            )

        result = copy.deepcopy(data_product)
        queue_event(DataProductDeletedEvent(before=data_product.to_event()))
        self.db.delete(data_product)
        self.db.commit()
        return result

    def update_data_product(
        self,
        id: UUID,
        data_product: DataProductUpdate,
    ) -> UpdateDataProductResponse:
        current_data_product = ensure_data_product_exists(
            id, self.db, options=[selectinload(DataProductModel.tags)]
        )
        before = current_data_product.to_event()
        update_data_product = data_product.model_dump(exclude_unset=True)

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

        self.db.commit()
        queue_event(
            DataProductUpdatedEvent(
                before=before, after=current_data_product.to_event()
            )
        )
        return UpdateDataProductResponse(id=current_data_product.id)

    def update_data_product_about(
        self,
        id: UUID,
        data_product: DataProductAboutUpdate,
    ) -> DataProductModel:
        current_data_product = ensure_data_product_exists(id, self.db)
        before = current_data_product.to_event()
        current_data_product.about = data_product.about
        self.db.commit()
        queue_event(
            DataProductUpdatedEvent(
                before=before, after=current_data_product.to_event()
            )
        )
        return current_data_product

    def update_data_product_status(
        self,
        id: UUID,
        data_product: DataProductStatusUpdate,
    ) -> DataProductModel:
        current_data_product = ensure_data_product_exists(id, self.db)
        before = current_data_product.to_event()
        current_data_product.status = data_product.status
        self.db.commit()
        queue_event(
            DataProductUpdatedEvent(
                before=before, after=current_data_product.to_event()
            )
        )
        return current_data_product

    def update_data_product_usage(
        self,
        id: UUID,
        usage: DataProductUsageUpdate,
    ) -> DataProductModel:
        # This method does not emit an event since we do not care about this in the infra
        current_data_product = ensure_data_product_exists(id, self.db)
        current_data_product.usage = usage.usage
        self.db.commit()
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
        data_outputs = (
            self.db.scalars(
                select(TechnicalAssetModel)
                .options(
                    joinedload(TechnicalAssetModel.dataset_links)
                    .selectinload(DataOutputDatasetAssociation.dataset)
                    .selectinload(DatasetModel.data_product_links)
                )
                .filter_by(owner_id=id)
                .execution_options(populate_existing=True)
            )
            .unique()
            .all()
        )

        for upstream_datasets in input_ports:
            nodes.append(
                Node(
                    id=upstream_datasets.id,
                    data=NodeData(
                        id=upstream_datasets.dataset_id,
                        name=upstream_datasets.dataset.name,
                        link_to_id=upstream_datasets.dataset.data_product_id,
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

        for data_output in data_outputs:
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
                    id=f"{data_output.id}-{product.id}",
                    source=product.id,
                    target=data_output.id,
                    animated=True,
                )
            )
            if level >= 2:
                for downstream_datasets in data_output.dataset_links:
                    nodes.append(
                        Node(
                            id=f"{downstream_datasets.dataset_id}_2",
                            data=NodeData(
                                id=f"{downstream_datasets.dataset_id}",
                                name=downstream_datasets.dataset.name,
                                link_to_id=downstream_datasets.dataset.data_product_id,
                            ),
                            type=NodeType.outputPortNode,
                        )
                    )
                    edges.append(
                        Edge(
                            id=f"{downstream_datasets.dataset_id}-{data_output.id}-2",
                            target=f"{downstream_datasets.dataset_id}_2",
                            source=data_output.id,
                            animated=downstream_datasets.status
                            == DecisionStatus.APPROVED,
                        )
                    )
                    if level >= 3:
                        for (
                            downstream_dps
                        ) in downstream_datasets.dataset.data_product_links:
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
                                        f"{downstream_datasets.dataset.id}-3"
                                    ),
                                    target=node_id,
                                    source=f"{downstream_datasets.dataset.id}_2",
                                    animated=downstream_dps.status
                                    == DecisionStatus.APPROVED,
                                )
                            )

        # if no data outputs are present, still show the children datasets
        if not data_outputs:
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
