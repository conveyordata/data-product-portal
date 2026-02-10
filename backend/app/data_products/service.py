import copy
from datetime import datetime
from typing import Optional, Sequence
from uuid import UUID
from warnings import deprecated

import pytz
from fastapi import HTTPException, status
from sqlalchemy import asc, select
from sqlalchemy.orm import Session, joinedload, selectinload

from app.authorization.role_assignments.enums import DecisionStatus
from app.authorization.roles.schema import Prototype
from app.configuration.data_product_lifecycles.model import (
    DataProductLifecycle as DataProductLifeCycleModel,
)
from app.configuration.tags.model import Tag as TagModel
from app.configuration.tags.model import ensure_tag_exists
from app.configuration.tags.schema import Tag
from app.core.aws.get_url import _get_data_product_role_arn
from app.core.namespace.validation import (
    NamespaceValidator,
    NamespaceValidityType,
    TechnicalAssetNamespaceValidator,
)
from app.data_products.model import DataProduct as DataProductModel
from app.data_products.model import ensure_data_product_exists
from app.data_products.output_port_technical_assets_link.model import (
    DataOutputDatasetAssociation,
)
from app.data_products.output_ports.enums import OutputPortAccessType
from app.data_products.output_ports.input_ports.model import (
    DataProductDatasetAssociation as DataProductDatasetModel,
)
from app.data_products.output_ports.model import Dataset as DatasetModel
from app.data_products.output_ports.model import ensure_output_port_exists
from app.data_products.output_ports.service import OutputPortService
from app.data_products.schema_request import (
    DataProductAboutUpdate,
    DataProductCreate,
    DataProductStatusUpdate,
    DataProductUpdate,
    DataProductUsageUpdate,
)
from app.data_products.schema_response import (
    DataProductGet,
    DataProductsGet,
    DatasetLinks,
    GetDataProductResponse,
    UpdateDataProductResponse,
)
from app.data_products.technical_assets.model import (
    TechnicalAsset as TechnicalAssetModel,
)
from app.data_products.technical_assets.schema_response import DataOutputGet
from app.graph.edge import Edge
from app.graph.graph import Graph
from app.graph.node import Node, NodeData, NodeType
from app.resource_names.service import ResourceNameService
from app.users.model import User as UserModel
from app.users.schema import User


class DataProductService:
    def __init__(self, db: Session):
        self.db = db
        self.namespace_validator = NamespaceValidator(DataProductModel)
        self.technical_asset_namespace_validator = TechnicalAssetNamespaceValidator()

    def get_input_ports(self, data_product_id: UUID) -> Sequence[DatasetLinks]:
        ensure_data_product_exists(data_product_id, self.db)
        return (
            self.db.scalars(
                select(DataProductDatasetModel)
                .options(
                    selectinload(DataProductDatasetModel.dataset),
                )
                .filter(DataProductDatasetModel.data_product_id == data_product_id),
            )
            .unique()
            .all()
        )

    def get_rolled_up_tags(self, data_product_id: UUID) -> set[Tag]:
        ensure_data_product_exists(data_product_id, self.db)
        rolled_up_tags = set()
        for output_ports in OutputPortService(self.db).get_output_ports(
            data_product_id
        ):
            rolled_up_tags.update(output_ports.tags)
        for technical_asset in self.get_data_outputs(data_product_id):
            rolled_up_tags.update(technical_asset.tags)
        return rolled_up_tags

    def get_data_product_old(self, id: UUID) -> DataProductGet:
        data_product = self.db.get(
            DataProductModel,
            id,
            options=[
                selectinload(DataProductModel.dataset_links)
                .selectinload(DataProductDatasetModel.dataset)
                .selectinload(DatasetModel.data_output_links),
                selectinload(DataProductModel.datasets).selectinload(DatasetModel.tags),
                selectinload(DataProductModel.datasets).raiseload("*"),
                selectinload(DataProductModel.data_outputs).selectinload(
                    TechnicalAssetModel.dataset_links
                ),
                selectinload(DataProductModel.data_outputs).selectinload(
                    TechnicalAssetModel.environment_configurations
                ),
            ],
        )
        default_lifecycle = self.db.scalar(
            select(DataProductLifeCycleModel).filter(
                DataProductLifeCycleModel.is_default
            )
        )

        rolled_up_tags = set()

        if not data_product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Data Product not found"
            )

        for link in data_product.dataset_links:
            rolled_up_tags.update(link.dataset.tags)
            for output_link in link.dataset.data_output_links:
                rolled_up_tags.update(output_link.data_output.tags)

        data_product.rolled_up_tags = rolled_up_tags

        if not data_product.lifecycle:
            data_product.lifecycle = default_lifecycle
        return data_product

    def get_data_product(self, id: UUID) -> GetDataProductResponse:
        data_product = self.db.get(
            DataProductModel,
            id,
        )
        default_lifecycle = self.db.scalar(
            select(DataProductLifeCycleModel).filter(
                DataProductLifeCycleModel.is_default
            )
        )

        if not data_product.lifecycle:
            data_product.lifecycle = default_lifecycle
        return data_product

    def get_data_products(
        self,
        filter_to_user_with_assigment: Optional[UUID] = None,
    ) -> Sequence[DataProductsGet]:
        default_lifecycle = self.db.scalar(
            select(DataProductLifeCycleModel).filter(
                DataProductLifeCycleModel.is_default
            )
        )
        query = select(DataProductModel).options(
            selectinload(DataProductModel.dataset_links).raiseload("*"),
            selectinload(DataProductModel.assignments).raiseload("*"),
            selectinload(DataProductModel.data_outputs).raiseload("*"),
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
        ) != NamespaceValidityType.VALID:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid namespace: {validity.value}",
            )

        data_product_schema = data_product.parse_pydantic_schema()
        tags = self._get_tags(data_product_schema.pop("tag_ids", []))
        _ = data_product_schema.pop("owners", [])
        model = DataProductModel(**data_product_schema, tags=tags)
        self.db.add(model)
        self.db.commit()
        return model

    def remove_data_product(self, id: UUID) -> DataProductModel:
        data_product = self.db.get(DataProductModel, id)
        if not data_product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Data Product {id} not found",
            )

        result = copy.deepcopy(data_product)
        self.db.delete(data_product)
        self.db.commit()
        return result

    def update_data_product(
        self,
        id: UUID,
        data_product: DataProductUpdate,
    ) -> UpdateDataProductResponse:
        current_data_product = ensure_data_product_exists(id, self.db)
        update_data_product = data_product.model_dump(exclude_unset=True)

        if (
            current_data_product.namespace != data_product.namespace
            and (
                validity := ResourceNameService(model=DataProductModel)
                .validate_resource_name(data_product.namespace, self.db)
                .validity
            )
            != NamespaceValidityType.VALID
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
        return UpdateDataProductResponse(id=current_data_product.id)

    def update_data_product_about(
        self,
        id: UUID,
        data_product: DataProductAboutUpdate,
    ) -> DataProductModel:
        current_data_product = ensure_data_product_exists(id, self.db)
        current_data_product.about = data_product.about
        self.db.commit()
        return current_data_product

    def update_data_product_status(
        self,
        id: UUID,
        data_product: DataProductStatusUpdate,
    ) -> DataProductModel:
        current_data_product = ensure_data_product_exists(id, self.db)
        current_data_product.status = data_product.status
        self.db.commit()
        return current_data_product

    def update_data_product_usage(
        self,
        id: UUID,
        usage: DataProductUsageUpdate,
    ) -> DataProductModel:
        current_data_product = ensure_data_product_exists(id, self.db)
        current_data_product.usage = usage.usage
        self.db.commit()
        return current_data_product

    def link_dataset_to_data_product(
        self,
        id: UUID,
        dataset_id: UUID,
        justification: str,
        *,
        actor: User,
    ) -> DataProductDatasetModel:
        """
        Links an output port to a data product to be used as input port.
        """

        dataset = ensure_output_port_exists(
            dataset_id,
            self.db,
            options=[
                selectinload(DatasetModel.data_product_links)
                .selectinload(DataProductDatasetModel.data_product)
                .selectinload(DataProductModel.dataset_links)
            ],
        )
        data_product = self.db.get(
            DataProductModel,
            id,
            options=[selectinload(DataProductModel.dataset_links)],
            populate_existing=True,
        )

        if dataset.id in [
            link.dataset_id
            for link in data_product.dataset_links
            if link.status != DecisionStatus.DENIED
        ]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Dataset {dataset_id} already exists in data product {id}",
            )
        if dataset.data_product_id == data_product.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot link own dataset to data product",
            )

        if not OutputPortService(self.db).is_visible_to_user(dataset, actor):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have access to this private dataset",
            )

        approval_status = (
            DecisionStatus.PENDING
            if dataset.access_type != OutputPortAccessType.PUBLIC
            else DecisionStatus.APPROVED
        )

        dataset_link = DataProductDatasetModel(
            dataset_id=dataset_id,
            status=approval_status,
            justification=justification,
            requested_by=actor,
            requested_on=datetime.now(tz=pytz.utc),
        )
        data_product.dataset_links.append(dataset_link)
        return dataset_link

    def link_datasets_to_data_product(
        self,
        id: UUID,
        dataset_ids: list[UUID],
        justification: str,
        *,
        actor: User,
    ) -> list[DataProductDatasetModel]:
        dataset_links = [
            self.link_dataset_to_data_product(
                id, dataset_id, justification, actor=actor
            )
            for dataset_id in dataset_ids
        ]
        self.db.commit()
        return dataset_links

    def unlink_dataset_from_data_product(
        self,
        id: UUID,
        dataset_id: UUID,
    ) -> DataProductDatasetModel:
        ensure_output_port_exists(dataset_id, self.db)
        data_product = ensure_data_product_exists(
            id, self.db, options=[selectinload(DataProductModel.dataset_links)]
        )
        data_product_dataset = next(
            (
                dataset
                for dataset in data_product.dataset_links
                if dataset.dataset_id == dataset_id
            ),
            None,
        )
        if not data_product_dataset:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Data product dataset for data product {id} not found",
            )

        data_product.dataset_links.remove(data_product_dataset)
        self.db.commit()
        return data_product_dataset

    @deprecated("Should use generate_signin_url instead")
    def get_data_product_role_arn(self, id: UUID, environment: str) -> str:
        return _get_data_product_role_arn(id, environment, self.db)

    def get_data_outputs(self, id: UUID) -> Sequence[DataOutputGet]:
        return (
            self.db.scalars(
                select(TechnicalAssetModel)
                .options(
                    selectinload(TechnicalAssetModel.environment_configurations),
                    selectinload(TechnicalAssetModel.dataset_links)
                    .selectinload(DataOutputDatasetAssociation.dataset)
                    .selectinload(DatasetModel.tags)
                    .raiseload("*"),
                )
                .filter(TechnicalAssetModel.owner_id == id)
            )
            .unique()
            .all()
        )

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

        dataset_links = (
            self.db.scalars(
                select(DataProductDatasetModel).filter_by(data_product_id=id)
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

        for upstream_datasets in dataset_links:
            nodes.append(
                Node(
                    id=upstream_datasets.id,
                    data=NodeData(
                        id=upstream_datasets.dataset_id,
                        name=upstream_datasets.dataset.name,
                    ),
                    type=NodeType.datasetNode,
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
                    type=NodeType.dataOutputNode,
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
                            ),
                            type=NodeType.datasetNode,
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
                            icon = downstream_dps.data_product.type.icon_key
                            nodes.append(
                                Node(
                                    id=f"{downstream_dps.id}_3",
                                    data=NodeData(
                                        id=f"{downstream_dps.data_product_id}",
                                        icon_key=icon,
                                        name=downstream_dps.data_product.name,
                                    ),
                                    type=NodeType.dataProductNode,
                                )
                            )
                            edges.append(
                                Edge(
                                    id=(
                                        f"{downstream_dps.id}-"
                                        f"{downstream_datasets.dataset.id}-3"
                                    ),
                                    target=f"{downstream_dps.id}_3",
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
                        ),
                        type=NodeType.datasetNode,
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
