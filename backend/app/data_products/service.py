import json
from datetime import datetime
from typing import List
from urllib import parse
from uuid import UUID

import httpx
import pytz
from botocore.exceptions import ClientError
from fastapi import HTTPException, status
from sqlalchemy import asc, select
from sqlalchemy.orm import Session, joinedload

from app.core.auth.credentials import AWSCredentials
from app.core.aws.boto3_clients import get_client
from app.core.aws.refresh_infrastructure_lambda import RefreshInfrastructureLambda
from app.core.conveyor.notebook_builder import CONVEYOR_SERVICE
from app.data_outputs.model import DataOutput as DataOutputModel
from app.data_outputs.schema_get import DataOutputGet
from app.data_outputs_datasets.enums import DataOutputDatasetLinkStatus
from app.data_product_memberships.enums import (
    DataProductMembershipStatus,
    DataProductUserRole,
)
from app.data_product_memberships.model import DataProductMembership
from app.data_product_memberships.schema import DataProductMembershipCreate
from app.data_products.model import DataProduct as DataProductModel
from app.data_products.model import ensure_data_product_exists
from app.data_products.schema import (
    DataProduct,
    DataProductAboutUpdate,
    DataProductCreate,
    DataProductUpdate,
)
from app.data_products.schema_get import DataProductGet, DataProductsGet
from app.data_products_datasets.enums import DataProductDatasetLinkStatus
from app.data_products_datasets.model import (
    DataProductDatasetAssociation as DataProductDatasetModel,
)
from app.data_products_datasets.schema import DataProductDatasetAssociationCreate
from app.datasets.enums import DatasetAccessType
from app.datasets.model import ensure_dataset_exists
from app.environment_platform_configurations.model import (
    EnvironmentPlatformConfiguration as EnvironmentPlatformConfigurationModel,
)
from app.environments.model import Environment as EnvironmentModel
from app.graph.edge import Edge
from app.graph.graph import Graph
from app.graph.node import Node, NodeData, NodeType
from app.platforms.model import Platform as PlatformModel
from app.tags.model import Tag as TagModel
from app.tags.model import ensure_tag_exists
from app.users.model import ensure_user_exists
from app.users.schema import User


class DataProductService:
    def get_data_product(self, id: UUID, db: Session) -> DataProductGet:
        data_product = (
            db.query(DataProductModel)
            .options(
                joinedload(DataProductModel.dataset_links),
            )
            .filter(DataProductModel.id == id)
            .first()
        )

        if not data_product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Data Product not found"
            )
        return data_product

    def get_data_products(self, db: Session) -> list[DataProductsGet]:
        return (
            db.query(DataProductModel)
            .options(
                joinedload(DataProductModel.dataset_links),
            )
            .order_by(asc(DataProductModel.name))
            .all()
        )

    def get_user_data_products(
        self, user_id: UUID, db: Session
    ) -> list[DataProductsGet]:
        return (
            db.query(DataProductModel)
            .options(
                joinedload(DataProductModel.memberships),
            )
            .filter(DataProductModel.memberships.any(user_id=user_id))
            .order_by(asc(DataProductModel.name))
            .all()
        )

    def _update_users(
        self,
        data_product: DataProductCreate,
        db: Session,
        memberships: list[DataProductMembershipCreate] = [],
    ) -> DataProductCreate:
        if not memberships:
            memberships = data_product.memberships
        data_product.memberships = []
        for membership in memberships:
            user = ensure_user_exists(membership.user_id, db)
            data_product.memberships.append(
                DataProductMembershipCreate(
                    user_id=user.id,
                    role=membership.role,
                )
            )
        return data_product

    def _update_datasets(
        self,
        data_product: DataProductCreate,
        db: Session,
        authenticated_user: User,
        dataset_links: list[DataProductDatasetAssociationCreate] = [],
    ) -> DataProductCreate:
        if not dataset_links:
            dataset_links = data_product.dataset_links
        data_product.dataset_links = []
        for dataset in dataset_links:
            dataset_model = ensure_dataset_exists(dataset.dataset_id, db)
            data_product.dataset_links.append(
                DataProductDatasetModel(
                    dataset_id=dataset_model.id,
                    status=DataProductDatasetLinkStatus.PENDING_APPROVAL,
                    requested_by_id=authenticated_user.id,
                    requested_on=datetime.now(tz=pytz.utc),
                )
            )
        return data_product

    def _fetch_tags(self, db: Session, tag_ids: list[UUID]) -> list[TagModel]:
        tags = []
        for tag_id in tag_ids:
            tag = ensure_tag_exists(tag_id, db)
            tags.append(tag)
        return tags

    def create_data_product(
        self, data_product: DataProductCreate, db: Session, authenticated_user: User
    ) -> dict[str, UUID]:
        data_product = self._update_users(data_product, db)
        data_product = data_product.parse_pydantic_schema()
        tags = self._fetch_tags(db, data_product.pop("tag_ids", []))
        data_product = DataProductModel(**data_product, tags=tags)
        for membership in data_product.memberships:
            membership.status = DataProductMembershipStatus.APPROVED
            membership.requested_by_id = authenticated_user.id
            membership.requested_on = datetime.now(tz=pytz.utc)
            membership.approved_by_id = authenticated_user.id
            membership.approved_on = datetime.now(tz=pytz.utc)

        db.add(data_product)
        db.commit()

        RefreshInfrastructureLambda().trigger()
        return {"id": data_product.id}

    def remove_data_product(self, id: UUID, db: Session):
        data_product = db.get(
            DataProductModel,
            id,
            options=[joinedload(DataProductModel.dataset_links)],
        )
        if not data_product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Data Product {id} not found",
            )
        data_product.memberships = []
        data_product.dataset_links = []
        for output in data_product.data_outputs:
            output.dataset_links = []
            output.delete()
        data_product.delete()
        db.commit()

    def _create_new_membership(
        self, user: User, role: DataProductUserRole
    ) -> DataProductMembership:
        return DataProductMembership(
            user_id=user.id,
            role=role,
            status=DataProductMembershipStatus.APPROVED,
            requested_by_id=user.id,
            requested_on=datetime.now(tz=pytz.utc),
            approved_by_id=user.id,
            approved_on=datetime.now(tz=pytz.utc),
        )

    def _update_memberships(
        self, data_product: DataProduct, membership_data: List[dict], db: Session
    ):
        existing_memberships = data_product.memberships
        request_user_ids = set(m["user_id"] for m in membership_data)

        for membership_item in membership_data:
            user = ensure_user_exists(membership_item["user_id"], db)
            membership = next(
                (m for m in existing_memberships if m.user_id == user.id),
                None,
            )
            if membership:
                membership.role = membership_item["role"]
            else:
                new_membership = self._create_new_membership(
                    user, membership_item["role"]
                )
                data_product.memberships.append(new_membership)

        memberships_to_remove = [
            m for m in existing_memberships if m.user_id not in request_user_ids
        ]
        for membership in memberships_to_remove:
            data_product.memberships.remove(membership)

        if not any(
            m.role == DataProductUserRole.OWNER for m in data_product.memberships
        ):
            raise ValueError("At least one owner membership is required.")

    def update_data_product(
        self, id: UUID, data_product: DataProductUpdate, db: Session
    ):
        current_data_product = ensure_data_product_exists(id, db)
        update_data_product = data_product.model_dump(exclude_unset=True)

        for k, v in update_data_product.items():
            if k == "memberships":
                self._update_memberships(current_data_product, v, db)
            elif k == "dataset_links":
                current_data_product.dataset_links = []
                for dataset in v:
                    dataset_model = ensure_dataset_exists(dataset.dataset_id, db)
                    dataset = DataProductDatasetModel(
                        dataset_id=dataset_model.id,
                        data_product_id=current_data_product.id,
                        status=dataset.status,
                        requested_by=dataset.requested_by,
                        requested_on=dataset.requested_on,
                        approved_by=dataset.approved_by,
                        approved_on=dataset.approved_on,
                        denied_by=dataset.denied_by,
                        denied_on=dataset.denied_on,
                    )
                    current_data_product.dataset_links.append(dataset)
            elif k == "tag_ids":
                new_tags = self._fetch_tags(db, v)
                current_data_product.tags = new_tags
            else:
                setattr(current_data_product, k, v) if v else None

        db.commit()
        RefreshInfrastructureLambda().trigger()
        return {"id": current_data_product.id}

    def update_data_product_about(
        self, id: UUID, data_product: DataProductAboutUpdate, db: Session
    ):
        current_data_product = ensure_data_product_exists(id, db)
        current_data_product.about = data_product.about
        db.commit()

    def link_dataset_to_data_product(
        self, id: UUID, dataset_id: UUID, authenticated_user: User, db: Session
    ):
        dataset = ensure_dataset_exists(dataset_id, db)
        data_product = ensure_data_product_exists(id, db)

        if dataset.id in [
            link.dataset_id
            for link in data_product.dataset_links
            if link.status != DataProductDatasetLinkStatus.DENIED
        ]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Dataset {dataset_id} already exists in data product {id}",
            )
        approval_status = (
            DataProductDatasetLinkStatus.PENDING_APPROVAL
            if dataset.access_type != DatasetAccessType.PUBLIC
            else DataProductDatasetLinkStatus.APPROVED
        )

        dataset_link = DataProductDatasetModel(
            dataset_id=dataset_id,
            status=approval_status,
            requested_by=authenticated_user,
            requested_on=datetime.now(tz=pytz.utc),
        )
        data_product.dataset_links.append(dataset_link)
        db.commit()
        db.refresh(data_product)
        RefreshInfrastructureLambda().trigger()
        return {"id": dataset_link.id}

    def unlink_dataset_from_data_product(self, id: UUID, dataset_id: UUID, db: Session):
        ensure_dataset_exists(dataset_id, db)
        data_product = ensure_data_product_exists(id, db)
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
        db.commit()
        RefreshInfrastructureLambda().trigger()

    def get_data_product_role_arn(self, id: UUID, environment: str, db: Session) -> str:
        environment_context = (
            db.query(EnvironmentModel)
            .get_one(EnvironmentModel.name, environment)
            .context
        )
        external_id = db.get(DataProductModel, id).external_id
        role_arn = environment_context.replace("{{}}", external_id)
        return role_arn

    def get_aws_temporary_credentials(
        self, role_arn: str, authenticated_user: User
    ) -> AWSCredentials:
        email = authenticated_user.email
        try:
            response = get_client("sts").assume_role(
                RoleArn=role_arn,
                RoleSessionName=email,
            )
        except ClientError:
            raise HTTPException(
                status_code=status.HTTP_501_NOT_IMPLEMENTED,
                detail="Please contact us on how to integrate with AWS",
            )

        return AWSCredentials(**response.get("Credentials"))

    def generate_signin_url(
        self, id: UUID, environment: str, authenticated_user: User, db: Session
    ) -> str:
        role = self.get_data_product_role_arn(id, environment, db)
        json_credentials = self.get_aws_temporary_credentials(role, authenticated_user)

        url_credentials = {}
        url_credentials["sessionId"] = json_credentials.AccessKeyId
        url_credentials["sessionKey"] = json_credentials.SecretAccessKey
        url_credentials["sessionToken"] = json_credentials.SessionToken
        json_dump = json.dumps(url_credentials)

        request_parameters = "?Action=getSigninToken"
        SESSION_DURATION = 900
        request_parameters += f"&SessionDuration={SESSION_DURATION}"
        request_parameters += f"&Session={parse.quote_plus(json_dump)}"
        request_url = "https://signin.aws.amazon.com/federation" + request_parameters

        r = httpx.get(request_url)

        signin_token = json.loads(r.text)

        request_parameters = "?Action=login"
        request_parameters += "&Issuer=portal.demo1.conveyordata.com"
        athena_link = "https://console.aws.amazon.com/athena/home#/query-editor"
        request_parameters += f"&Destination={parse.quote_plus(athena_link)}"
        request_parameters += f"&SigninToken={signin_token['SigninToken']}"
        request_url = "https://signin.aws.amazon.com/federation" + request_parameters

        return request_url

    def get_conveyor_ide_url(self, id: UUID, db: Session) -> str:
        data_product = db.get(DataProductModel, id)
        return CONVEYOR_SERVICE.generate_ide_url(data_product.external_id)

    def get_data_outputs(self, id: UUID, db: Session) -> list[DataOutputGet]:
        return db.query(DataOutputModel).filter(DataOutputModel.owner_id == id).all()

    def get_databricks_workspace_url(
        self, id: UUID, environment: str, db: Session
    ) -> str:
        data_product = db.get(DataProductModel, id)
        environment_model = db.scalar(
            select(EnvironmentModel).where(EnvironmentModel.name == environment)
        )
        platform = db.scalar(
            select(PlatformModel).where(PlatformModel.name == "Databricks")
        )

        stmt = select(EnvironmentPlatformConfigurationModel).where(
            EnvironmentPlatformConfigurationModel.environment_id
            == environment_model.id,
            EnvironmentPlatformConfigurationModel.platform_id == platform.id,
        )
        config = db.scalar(stmt)
        if not config:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=(
                    "Workspace not configured for business"
                    f"area {data_product.business_area.name}"
                ),
            )

        config = json.loads(config.config)["workspace_urls"]
        if not str(data_product.business_area_id) in config:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=(
                    "Workspace not configured for business"
                    f"area {data_product.business_area.name}"
                ),
            )
        return config[str(data_product.business_area_id)]

    def get_graph_data(self, id: UUID, level: int, db: Session) -> Graph:
        product = db.get(DataProductModel, id)
        nodes = [
            Node(
                id=id,
                isMain=True,
                data=NodeData(id=id, name=product.name, icon_key=product.type.icon_key),
                type=NodeType.dataProductNode,
            )
        ]
        edges = []
        for upstream_datasets in product.dataset_links:
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
                    animated=upstream_datasets.status
                    == DataProductDatasetLinkStatus.APPROVED,
                )
            )

        for data_output in product.data_outputs:
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
                            == DataOutputDatasetLinkStatus.APPROVED,
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
                                    == DataProductDatasetLinkStatus.APPROVED,
                                )
                            )

        return Graph(nodes=set(nodes), edges=set(edges))
