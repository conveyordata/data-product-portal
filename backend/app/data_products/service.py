import json
from datetime import datetime
from typing import Sequence
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
from app.core.namespace.validation import (
    DataOutputNamespaceValidator,
    NamespaceLengthLimits,
    NamespaceSuggestion,
    NamespaceValidation,
    NamespaceValidator,
    NamespaceValidityType,
)
from app.data_outputs.model import DataOutput as DataOutputModel
from app.data_outputs.schema_response import DataOutputGet
from app.data_outputs_datasets.model import DataOutputDatasetAssociation
from app.data_product_lifecycles.model import (
    DataProductLifecycle as DataProductLifeCycleModel,
)
from app.data_products.model import DataProduct as DataProductModel
from app.data_products.model import ensure_data_product_exists
from app.data_products.schema_request import (
    DataProductAboutUpdate,
    DataProductCreate,
    DataProductStatusUpdate,
    DataProductUpdate,
)
from app.data_products.schema_response import DataProductGet, DataProductsGet
from app.data_products_datasets.model import (
    DataProductDatasetAssociation as DataProductDatasetModel,
)
from app.datasets.enums import DatasetAccessType
from app.datasets.model import Dataset as DatasetModel
from app.datasets.model import ensure_dataset_exists
from app.datasets.service import DatasetService
from app.environment_platform_configurations.model import (
    EnvironmentPlatformConfiguration as EnvironmentPlatformConfigurationModel,
)
from app.environments.model import Environment as EnvironmentModel
from app.graph.edge import Edge
from app.graph.graph import Graph
from app.graph.node import Node, NodeData, NodeType
from app.platforms.model import Platform as PlatformModel
from app.role_assignments.enums import DecisionStatus
from app.roles.schema import Prototype
from app.tags.model import Tag as TagModel
from app.tags.model import ensure_tag_exists
from app.users.model import User as UserModel
from app.users.schema import User


class DataProductService:
    def __init__(self, db: Session):
        self.db = db
        self.namespace_validator = NamespaceValidator(DataProductModel)
        self.data_output_namespace_validator = DataOutputNamespaceValidator()

    def get_data_product(self, id: UUID) -> DataProductGet:
        data_product = self.db.get(
            DataProductModel,
            id,
            options=[
                joinedload(DataProductModel.dataset_links)
                .joinedload(DataProductDatasetModel.dataset)
                .joinedload(DatasetModel.data_output_links),
                joinedload(DataProductModel.data_outputs).joinedload(
                    DataOutputModel.dataset_links
                ),
            ],
        )
        print(data_product.dataset_links)

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

        print(data_product.dataset_links)

        for link in data_product.dataset_links:
            rolled_up_tags.update(link.dataset.tags)
            for output_link in link.dataset.data_output_links:
                rolled_up_tags.update(output_link.data_output.tags)

        data_product.rolled_up_tags = rolled_up_tags

        if not data_product.lifecycle:
            data_product.lifecycle = default_lifecycle
        return data_product

    def get_data_products(self) -> Sequence[DataProductsGet]:
        default_lifecycle = self.db.scalar(
            select(DataProductLifeCycleModel).filter(
                DataProductLifeCycleModel.is_default
            )
        )
        dps = (
            self.db.scalars(
                select(DataProductModel)
                .options(
                    joinedload(DataProductModel.dataset_links).raiseload("*"),
                    joinedload(DataProductModel.assignments).raiseload("*"),
                    joinedload(DataProductModel.data_outputs).raiseload("*"),
                )
                .order_by(asc(DataProductModel.name))
            )
            .unique()
            .all()
        )

        for dp in dps:
            if not dp.lifecycle:
                dp.lifecycle = default_lifecycle
        return dps

    def get_owners(self, id: UUID) -> Sequence[User]:
        data_product = ensure_data_product_exists(
            id,
            self.db,
            options=[joinedload(DataProductModel.assignments)],
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

    def get_user_data_products(self, user_id: UUID) -> Sequence[DataProductsGet]:
        return (
            self.db.scalars(
                select(DataProductModel)
                .options(
                    joinedload(DataProductModel.dataset_links).raiseload("*"),
                    joinedload(DataProductModel.assignments).raiseload("*"),
                    joinedload(DataProductModel.data_outputs).raiseload("*"),
                )
                .filter(
                    DataProductModel.assignments.any(
                        user_id=user_id, decision=DecisionStatus.APPROVED
                    )
                )
                .order_by(asc(DataProductModel.name))
            )
            .unique()
            .all()
        )

    def _get_tags(self, tag_ids: list[UUID]) -> list[TagModel]:
        return [ensure_tag_exists(tag_id, self.db) for tag_id in tag_ids]

    def create_data_product(
        self,
        data_product: DataProductCreate,
    ) -> DataProductModel:
        if (
            validity := self.namespace_validator.validate_namespace(
                data_product.namespace, self.db
            ).validity
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

        RefreshInfrastructureLambda().trigger()
        return model

    def remove_data_product(self, id: UUID) -> None:
        data_product = self.db.get(DataProductModel, id)
        if not data_product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Data Product {id} not found",
            )

        self.db.delete(data_product)
        self.db.commit()

    def update_data_product(
        self, id: UUID, data_product: DataProductUpdate
    ) -> dict[str, UUID]:
        current_data_product = ensure_data_product_exists(id, self.db)
        update_data_product = data_product.model_dump(exclude_unset=True)

        if (
            current_data_product.namespace != data_product.namespace
            and (
                validity := self.namespace_validator.validate_namespace(
                    data_product.namespace, self.db
                ).validity
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
        RefreshInfrastructureLambda().trigger()
        return {"id": current_data_product.id}

    def update_data_product_about(
        self, id: UUID, data_product: DataProductAboutUpdate
    ) -> None:
        current_data_product = ensure_data_product_exists(id, self.db)
        current_data_product.about = data_product.about
        self.db.commit()

    def update_data_product_status(
        self, id: UUID, data_product: DataProductStatusUpdate
    ) -> None:
        current_data_product = ensure_data_product_exists(id, self.db)
        current_data_product.status = data_product.status
        self.db.commit()

    def link_dataset_to_data_product(
        self,
        id: UUID,
        dataset_id: UUID,
        actor: User,
    ) -> DataProductDatasetModel:
        dataset = ensure_dataset_exists(
            dataset_id,
            self.db,
            options=[
                joinedload(DatasetModel.data_product_links)
                .joinedload(DataProductDatasetModel.data_product)
                .joinedload(DataProductModel.dataset_links)
            ],
        )
        data_product = self.db.get(
            DataProductModel,
            id,
            options=[joinedload(DataProductModel.dataset_links)],
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

        if not DatasetService(self.db).is_visible_to_user(dataset, actor):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have access to this private dataset",
            )

        approval_status = (
            DecisionStatus.PENDING
            if dataset.access_type != DatasetAccessType.PUBLIC
            else DecisionStatus.APPROVED
        )

        dataset_link = DataProductDatasetModel(
            dataset_id=dataset_id,
            status=approval_status,
            requested_by=actor,
            requested_on=datetime.now(tz=pytz.utc),
        )
        data_product.dataset_links.append(dataset_link)
        self.db.commit()
        self.db.refresh(data_product)
        RefreshInfrastructureLambda().trigger()
        return dataset_link

    def unlink_dataset_from_data_product(self, id: UUID, dataset_id: UUID) -> None:
        ensure_dataset_exists(dataset_id, self.db)
        data_product = ensure_data_product_exists(
            id, self.db, options=[joinedload(DataProductModel.dataset_links)]
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
        RefreshInfrastructureLambda().trigger()

    def get_data_product_role_arn(self, id: UUID, environment: str) -> str:
        environment_context = (
            self.db.execute(
                select(EnvironmentModel).where(EnvironmentModel.name == environment)
            )
            .scalar_one()
            .context
        )
        namespace = self.db.get(DataProductModel, id).namespace
        role_arn = environment_context.replace("{{}}", namespace)
        return role_arn

    @classmethod
    def get_aws_temporary_credentials(
        cls, role_arn: str, actor: User
    ) -> AWSCredentials:
        email = actor.email
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
        self, id: UUID, environment: str, authenticated_user: User
    ) -> str:
        role = self.get_data_product_role_arn(id, environment)
        json_credentials = self.get_aws_temporary_credentials(role, authenticated_user)

        url_credentials = {
            "sessionId": json_credentials.AccessKeyId,
            "sessionKey": json_credentials.SecretAccessKey,
            "sessionToken": json_credentials.SessionToken,
        }
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

    def get_conveyor_ide_url(self, id: UUID) -> str:
        data_product = self.db.get(DataProductModel, id)
        return CONVEYOR_SERVICE.generate_ide_url(data_product.namespace)

    def get_data_outputs(self, id: UUID) -> Sequence[DataOutputGet]:
        return (
            self.db.scalars(
                select(DataOutputModel)
                .options(
                    joinedload(DataOutputModel.environment_configurations),
                    joinedload(DataOutputModel.dataset_links)
                    .joinedload(DataOutputDatasetAssociation.dataset)
                    .raiseload("*"),
                )
                .filter(DataOutputModel.owner_id == id)
            )
            .unique()
            .all()
        )

    def get_env_platform_config(
        self, id: UUID, environment: str, platform_name: str
    ) -> str:
        environment_model = self.db.scalar(
            select(EnvironmentModel).where(EnvironmentModel.name == environment)
        )
        platform = self.db.scalar(
            select(PlatformModel).where(PlatformModel.name == platform_name)
        )

        stmt = select(EnvironmentPlatformConfigurationModel).where(
            EnvironmentPlatformConfigurationModel.environment_id
            == environment_model.id,
            EnvironmentPlatformConfigurationModel.platform_id == platform.id,
        )
        config = self.db.scalar(stmt)
        if not config:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=(
                    f"Missing Platform Environment configuration for {platform_name}"
                ),
            )
        return config.config

    def get_databricks_workspace_url(self, id: UUID, environment: str) -> str:
        platform_config = self.get_env_platform_config(id, environment, "Databricks")
        data_product = self.db.get(DataProductModel, id)
        config = json.loads(platform_config)["workspace_urls"]
        if not str(data_product.domain_id) in config:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=(
                    "Workspace not configured for" f"domain {data_product.domain.name}"
                ),
            )
        return config[str(data_product.domain_id)]

    def get_snowflake_url(self, id: UUID, environment: str) -> str:
        config = json.loads(self.get_env_platform_config(id, environment, "Snowflake"))
        if "login_url" not in config.keys():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=("login_url missing from Snowflake configuration"),
            )
        return config["login_url"]

    def get_graph_data(self, id: UUID, level: int) -> Graph:
        product = self.db.get(
            DataProductModel,
            id,
            options=[
                joinedload(DataProductModel.dataset_links),
                joinedload(DataProductModel.data_outputs)
                .joinedload(DataOutputModel.dataset_links)
                .joinedload(DataOutputDatasetAssociation.dataset)
                .joinedload(DatasetModel.data_product_links),
            ],
            # As this is also called from the DataOutputService, we need to ensure
            # that the DataOutput for which this is called is not loaded from cache,
            # but instead loaded anew with all necessary fields eagerly loaded
            populate_existing=True,
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
                    animated=upstream_datasets.status == DecisionStatus.APPROVED,
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

        return Graph(nodes=set(nodes), edges=set(edges))

    def validate_data_product_namespace(self, namespace: str) -> NamespaceValidation:
        return self.namespace_validator.validate_namespace(namespace, self.db)

    @classmethod
    def data_product_namespace_suggestion(cls, name: str) -> NamespaceSuggestion:
        return NamespaceValidator.namespace_suggestion(name)

    @classmethod
    def data_product_namespace_length_limits(cls) -> NamespaceLengthLimits:
        return NamespaceValidator.namespace_length_limits()

    def validate_data_output_namespace(
        self, namespace: str, data_product_id: UUID
    ) -> NamespaceValidation:
        return self.data_output_namespace_validator.validate_namespace(
            namespace, self.db, data_product_id
        )
