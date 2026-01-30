from copy import deepcopy
from typing import Optional, Sequence
from uuid import UUID

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.authorization.role_assignments.data_product.auth import (
    DataProductAuthAssignment,
)
from app.authorization.role_assignments.data_product.schema import (
    UpdateRoleAssignment,
)
from app.authorization.role_assignments.data_product.service import (
    RoleAssignmentService,
)
from app.authorization.role_assignments.enums import DecisionStatus
from app.authorization.role_assignments.output_port.service import (
    RoleAssignmentService as DatasetRoleAssignmentService,
)
from app.authorization.roles.schema import Prototype, Scope
from app.authorization.roles.service import RoleService
from app.configuration.data_product_settings.service import DataProductSettingService
from app.core.auth.auth import get_authenticated_user
from app.core.authz import Action, Authorization, DataProductResolver
from app.core.authz.resolvers import EmptyResolver
from app.core.aws.refresh_infrastructure_lambda import RefreshInfrastructureLambda
from app.core.namespace.validation import (
    NamespaceLengthLimits,
    NamespaceSuggestion,
    NamespaceValidation,
)
from app.data_products import email
from app.data_products.model import DataProduct as DataProductModel
from app.data_products.output_ports.enums import OutputPortAccessType
from app.data_products.output_ports.input_ports.model import (
    DataProductDatasetAssociation,
)
from app.data_products.output_ports.service import OutputPortService
from app.data_products.schema_request import (
    DataProductAboutUpdate,
    DataProductCreate,
    DataProductStatusUpdate,
    DataProductUpdate,
    DataProductUsageUpdate,
    LinkDatasetsToDataProduct,
    LinkInputPortsToDataProduct,
)
from app.data_products.schema_response import (
    CreateDataProductResponse,
    CreateTechnicalAssetResponse,
    DataProductGet,
    DataProductsGet,
    DatasetLinks,
    GetConveyorIdeUrlResponse,
    GetDatabricksWorkspaceUrlResponse,
    GetDataProductInputPortsResponse,
    GetDataProductResponse,
    GetDataProductRolledUpTagsResponse,
    GetDataProductsResponse,
    GetSigninUrlResponse,
    GetSnowflakeUrlResponse,
    LinkDatasetsToDataProductPost,
    LinkInputPortsToDataProductPost,
    UpdateDataProductResponse,
)
from app.data_products.service import DataProductService
from app.data_products.technical_assets.schema_request import (
    CreateTechnicalAssetRequest,
    DataOutputCreate,
)
from app.data_products.technical_assets.schema_response import (
    DataOutputGet,
    GetTechnicalAssetsResponse,
)
from app.data_products.technical_assets.service import DataOutputService
from app.database.database import get_db_session
from app.events.enums import EventReferenceEntity, EventType
from app.events.schema import CreateEvent
from app.events.schema_response import (
    GetEventHistoryResponse,
    GetEventHistoryResponseItemOld,
)
from app.events.service import EventService
from app.graph.graph import Graph
from app.resource_names.service import (
    DataOutputResourceNameValidator,
    ResourceNameService,
)
from app.users.notifications.service import NotificationService
from app.users.schema import User

router = APIRouter()


@router.get("/namespace_suggestion", deprecated=True)
def get_data_product_namespace_suggestion(name: str) -> NamespaceSuggestion:
    return NamespaceSuggestion(
        namespace=ResourceNameService.resource_name_suggestion(name).resource_name
    )


@router.get("/validate_namespace", deprecated=True)
def validate_data_product_namespace(
    namespace: str, db: Session = Depends(get_db_session)
) -> NamespaceValidation:
    return NamespaceValidation(
        validity=ResourceNameService(model=DataProductModel)
        .validate_resource_name(namespace, db)
        .validity
    )


@router.get("/namespace_length_limits", deprecated=True)
def get_data_product_namespace_length_limits() -> NamespaceLengthLimits:
    return NamespaceLengthLimits(
        max_length=ResourceNameService.resource_name_length_limits().max_length
    )


@router.post(
    "",
    responses={
        200: {
            "description": "Data Product successfully created",
            "content": {
                "application/json": {
                    "example": {"id": "random id of the new data_product"}
                }
            },
        },
        404: {
            "description": "Owner not found",
            "content": {
                "application/json": {
                    "example": {"detail": "User id for owner not found"}
                }
            },
        },
    },
    dependencies=[
        Depends(Authorization.enforce(Action.GLOBAL__CREATE_DATAPRODUCT, EmptyResolver))
    ],
)
def create_data_product(
    data_product: DataProductCreate,
    db: Session = Depends(get_db_session),
    authenticated_user: User = Depends(get_authenticated_user),
) -> CreateDataProductResponse:
    created_data_product = DataProductService(db).create_data_product(data_product)
    owners = data_product.owners
    _assign_owner_role_assignments(
        created_data_product.id,
        owners=owners,
        db=db,
        actor=authenticated_user,
    )

    event_id = EventService(db).create_event(
        CreateEvent(
            name=EventType.DATA_PRODUCT_CREATED,
            subject_id=created_data_product.id,
            subject_type=EventReferenceEntity.DATA_PRODUCT,
            actor_id=authenticated_user.id,
        ),
    )
    NotificationService(db).create_data_product_notifications(
        data_product_id=created_data_product.id,
        event_id=event_id,
        extra_receiver_ids=owners,
    )
    RefreshInfrastructureLambda().trigger()
    OutputPortService(db).recalculate_search_for_output_ports_of_product(
        created_data_product.id
    )
    return CreateDataProductResponse(id=created_data_product.id)


def _assign_owner_role_assignments(
    data_product_id: UUID, owners: Sequence[UUID], db: Session, actor: User
) -> None:
    owner_role = RoleService(db).find_prototype(Scope.DATA_PRODUCT, Prototype.OWNER)
    if not owner_role:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Owner role not found",
        )

    assignment_service = RoleAssignmentService(db)
    for owner_id in owners:
        response = assignment_service.create_assignment(
            data_product_id,
            user_id=owner_id,
            role_id=owner_role.id,
            actor=actor,
        )
        assignment = assignment_service.update_assignment(
            UpdateRoleAssignment(id=response.id, decision=DecisionStatus.APPROVED),
            actor=actor,
        )
        DataProductAuthAssignment(assignment).add()
        EventService(db).create_event(
            CreateEvent(
                name=EventType.DATA_PRODUCT_ROLE_ASSIGNMENT_CREATED,
                subject_id=response.data_product_id,
                subject_type=EventReferenceEntity.DATA_PRODUCT,
                target_id=response.user_id,
                target_type=EventReferenceEntity.USER,
                actor_id=actor.id,
            )
        )


@router.delete(
    "/{id}",
    responses={
        404: {
            "description": "Data Product not found",
            "content": {
                "application/json": {"example": {"detail": "Data Product id not found"}}
            },
        }
    },
    dependencies=[
        Depends(
            Authorization.enforce(Action.DATA_PRODUCT__DELETE, DataProductResolver)
        ),
    ],
)
def remove_data_product(
    id: UUID,
    db: Session = Depends(get_db_session),
    authenticated_user: User = Depends(get_authenticated_user),
) -> None:
    data_product = DataProductService(db).remove_data_product(id)
    Authorization().clear_assignments_for_resource(resource_id=str(id))

    event_id = EventService(db).create_event(
        CreateEvent(
            name=EventType.DATA_PRODUCT_REMOVED,
            actor_id=authenticated_user.id,
            subject_id=data_product.id,
            subject_type=EventReferenceEntity.DATA_PRODUCT,
            deleted_subject_identifier=data_product.name,
        ),
    )
    NotificationService(db).create_data_product_notifications(
        data_product_id=data_product.id, event_id=event_id
    )


@router.put(
    "/{id}",
    responses={
        404: {
            "description": "Data Product not found",
            "content": {
                "application/json": {"example": {"detail": "Data Product id not found"}}
            },
        }
    },
    dependencies=[
        Depends(
            Authorization.enforce(
                Action.DATA_PRODUCT__UPDATE_PROPERTIES, DataProductResolver
            )
        ),
    ],
)
def update_data_product(
    id: UUID,
    data_product: DataProductUpdate,
    db: Session = Depends(get_db_session),
    authenticated_user: User = Depends(get_authenticated_user),
) -> UpdateDataProductResponse:
    result = DataProductService(db).update_data_product(id, data_product)
    EventService(db).create_event(
        CreateEvent(
            name=EventType.DATA_PRODUCT_UPDATED,
            subject_id=id,
            subject_type=EventReferenceEntity.DATA_PRODUCT,
            actor_id=authenticated_user.id,
        )
    )
    RefreshInfrastructureLambda().trigger()
    OutputPortService(db).recalculate_search_for_output_ports_of_product(id)
    return result


@router.put(
    "/{id}/about",
    responses={
        404: {
            "description": "Data Product not found",
            "content": {
                "application/json": {"example": {"detail": "Data Product id not found"}}
            },
        }
    },
    dependencies=[
        Depends(
            Authorization.enforce(
                Action.DATA_PRODUCT__UPDATE_PROPERTIES, DataProductResolver
            )
        ),
    ],
)
def update_data_product_about(
    id: UUID,
    data_product: DataProductAboutUpdate,
    db: Session = Depends(get_db_session),
    authenticated_user: User = Depends(get_authenticated_user),
) -> None:
    data_product = DataProductService(db).update_data_product_about(id, data_product)
    EventService(db).create_event(
        CreateEvent(
            name=EventType.DATA_PRODUCT_UPDATED,
            subject_id=data_product.id,
            subject_type=EventReferenceEntity.DATA_PRODUCT,
            actor_id=authenticated_user.id,
        )
    )


@router.put(
    "/{id}/status",
    responses={
        404: {
            "description": "Data Product not found",
            "content": {
                "application/json": {"example": {"detail": "Data Product id not found"}}
            },
        }
    },
    dependencies=[
        Depends(
            Authorization.enforce(
                Action.DATA_PRODUCT__UPDATE_STATUS, DataProductResolver
            )
        ),
    ],
)
def update_data_product_status(
    id: UUID,
    data_product: DataProductStatusUpdate,
    db: Session = Depends(get_db_session),
    authenticated_user: User = Depends(get_authenticated_user),
) -> None:
    data_product = DataProductService(db).update_data_product_status(id, data_product)
    EventService(db).create_event(
        CreateEvent(
            name=EventType.DATA_PRODUCT_UPDATED,
            subject_id=data_product.id,
            subject_type=EventReferenceEntity.DATA_PRODUCT,
            actor_id=authenticated_user.id,
        )
    )


@router.put(
    "/{id}/usage",
    dependencies=[
        Depends(
            Authorization.enforce(
                Action.DATA_PRODUCT__UPDATE_PROPERTIES, DataProductResolver
            )
        ),
    ],
)
def update_data_product_usage(
    id: UUID,
    usage: DataProductUsageUpdate,
    db: Session = Depends(get_db_session),
    authenticated_user: User = Depends(get_authenticated_user),
) -> None:
    DataProductService(db).update_data_product_usage(id, usage)
    EventService(db).create_event(
        CreateEvent(
            name=EventType.DATA_PRODUCT_UPDATED,
            subject_id=id,
            subject_type=EventReferenceEntity.DATA_PRODUCT,
            actor_id=authenticated_user.id,
        )
    )


def _send_dataset_link_emails(
    dataset_links: list[DataProductDatasetAssociation],
    background_tasks: BackgroundTasks,
    actor: User,
    db: Session,
) -> None:
    for dataset_link in dataset_links:
        if dataset_link.dataset.access_type != OutputPortAccessType.PUBLIC:
            approvers = DatasetRoleAssignmentService(db).users_with_authz_action(
                dataset_link.dataset_id,
                Action.OUTPUT_PORT__APPROVE_DATAPRODUCT_ACCESS_REQUEST,
            )
            background_tasks.add_task(
                email.send_dataset_link_email(
                    dataset_link.data_product,
                    dataset_link.dataset,
                    requester=deepcopy(actor),
                    approvers=[deepcopy(approver) for approver in approvers],
                )
            )


@router.get("/{id}/graph")
def get_data_product_graph_data(
    id: UUID, db: Session = Depends(get_db_session), level: int = 3
) -> Graph:
    return DataProductService(db).get_graph_data(id, level)


@router.post(
    "/{id}/settings/{setting_id}",
    dependencies=[
        Depends(
            Authorization.enforce(
                Action.DATA_PRODUCT__UPDATE_SETTINGS, DataProductResolver
            )
        ),
    ],
)
def set_value_for_data_product(
    id: UUID,
    setting_id: UUID,
    value: str,
    db: Session = Depends(get_db_session),
    authenticated_user: User = Depends(get_authenticated_user),
) -> None:
    DataProductSettingService(db).set_value_for_product(setting_id, id, value)
    EventService(db).create_event(
        CreateEvent(
            name=EventType.DATA_PRODUCT_SETTING_UPDATED,
            subject_id=id,
            subject_type=EventReferenceEntity.DATA_PRODUCT,
            actor_id=authenticated_user.id,
        )
    )
    RefreshInfrastructureLambda().trigger()


_router = router
router = APIRouter(tags=["Data products"])
old_route = "/data_products"
route = "/v2/data_products"
router.include_router(_router, prefix=old_route, deprecated=True)
router.include_router(_router, prefix=route)


@router.post(
    f"{old_route}/{{id}}/dataset/{{dataset_id}}",
    responses={
        400: {
            "description": "Dataset not found",
            "content": {
                "application/json": {"example": {"detail": "Dataset not found"}}
            },
        },
        404: {
            "description": "Data Product not found",
            "content": {
                "application/json": {"example": {"detail": "Data Product id not found"}}
            },
        },
    },
    dependencies=[
        Depends(
            Authorization.enforce(
                Action.DATA_PRODUCT__REQUEST_OUTPUT_PORT_ACCESS,
                DataProductResolver,
            )
        ),
    ],
    deprecated=True,
)
def link_dataset_to_data_product(
    id: UUID,
    dataset_id: UUID,
    background_tasks: BackgroundTasks,
    authenticated_user: User = Depends(get_authenticated_user),
    db: Session = Depends(get_db_session),
) -> dict[str, UUID]:
    response = link_datasets_to_data_product(
        id,
        LinkDatasetsToDataProduct(
            dataset_ids=[dataset_id],
            justification="No justification provided. (deprecated endpoint used)",
        ),
        background_tasks,
        authenticated_user,
        db,
    )
    return {"id": response.dataset_links[0]}


@router.post(
    f"{old_route}/{{id}}/link_datasets",
    responses={
        400: {
            "description": "Dataset not found",
            "content": {
                "application/json": {"example": {"detail": "Dataset not found"}}
            },
        },
        404: {
            "description": "Data Product not found",
            "content": {
                "application/json": {"example": {"detail": "Data Product id not found"}}
            },
        },
    },
    dependencies=[
        Depends(
            Authorization.enforce(
                Action.DATA_PRODUCT__REQUEST_OUTPUT_PORT_ACCESS,
                DataProductResolver,
            )
        ),
    ],
    deprecated=True,
)
def link_datasets_to_data_product(
    id: UUID,
    link_datasets: LinkDatasetsToDataProduct,
    background_tasks: BackgroundTasks,
    authenticated_user: User = Depends(get_authenticated_user),
    db: Session = Depends(get_db_session),
) -> LinkDatasetsToDataProductPost:
    response = link_input_ports_to_data_product(
        id,
        link_input_ports=LinkInputPortsToDataProduct(
            input_ports=link_datasets.dataset_ids,
            justification=link_datasets.justification,
        ),
        background_tasks=background_tasks,
        db=db,
        authenticated_user=authenticated_user,
    )
    return LinkDatasetsToDataProductPost(dataset_links=response.input_port_links)


@router.post(
    f"{route}/{{id}}/link_input_ports",
    responses={
        400: {
            "description": "Output port not found",
            "content": {
                "application/json": {"example": {"detail": "Output port not found"}}
            },
        },
        404: {
            "description": "Data Product not found",
            "content": {
                "application/json": {"example": {"detail": "Data Product id not found"}}
            },
        },
    },
    dependencies=[
        Depends(
            Authorization.enforce(
                Action.DATA_PRODUCT__REQUEST_OUTPUT_PORT_ACCESS,
                DataProductResolver,
            )
        ),
    ],
)
def link_input_ports_to_data_product(
    id: UUID,
    link_input_ports: LinkInputPortsToDataProduct,
    background_tasks: BackgroundTasks,
    authenticated_user: User = Depends(get_authenticated_user),
    db: Session = Depends(get_db_session),
) -> LinkInputPortsToDataProductPost:
    dataset_links = DataProductService(db).link_datasets_to_data_product(
        id,
        link_input_ports.input_ports,
        link_input_ports.justification,
        actor=authenticated_user,
    )

    event_ids = EventService(db).create_events(
        [
            CreateEvent(
                name=(
                    EventType.DATA_PRODUCT_DATASET_LINK_REQUESTED
                    if dataset_link.status == DecisionStatus.PENDING
                    else EventType.DATA_PRODUCT_DATASET_LINK_APPROVED
                ),
                subject_id=dataset_link.data_product_id,
                subject_type=EventReferenceEntity.DATA_PRODUCT,
                target_id=dataset_link.dataset_id,
                target_type=EventReferenceEntity.DATASET,
                actor_id=authenticated_user.id,
            )
            for dataset_link in dataset_links
        ]
    )
    for dataset_link, event_id in zip(dataset_links, event_ids):
        if dataset_link.status == DecisionStatus.APPROVED:
            NotificationService(db).create_data_product_notifications(
                data_product_id=dataset_link.data_product_id, event_id=event_id
            )

    _send_dataset_link_emails(dataset_links, background_tasks, authenticated_user, db)
    RefreshInfrastructureLambda().trigger()
    return LinkInputPortsToDataProductPost(
        input_port_links=[dataset_link.id for dataset_link in dataset_links]
    )


@router.get(old_route, deprecated=True)
def get_data_products_old(
    db: Session = Depends(get_db_session),
    filter_to_user_with_assigment: Optional[UUID] = None,
) -> Sequence[DataProductsGet]:
    return DataProductService(db).get_data_products(
        filter_to_user_with_assigment=filter_to_user_with_assigment
    )


@router.get(route)
def get_data_products(
    db: Session = Depends(get_db_session),
    filter_to_user_with_assigment: Optional[UUID] = None,
) -> GetDataProductsResponse:
    return GetDataProductsResponse(
        data_products=[
            DataProductsGet.model_validate(data_product_old).convert()
            for data_product_old in get_data_products_old(
                db, filter_to_user_with_assigment
            )
        ]
    )


@router.get(f"{old_route}/{{id}}/history", deprecated=True)
def get_event_history_old(
    id: UUID, db: Session = Depends(get_db_session)
) -> Sequence[GetEventHistoryResponseItemOld]:
    return EventService(db).get_history(id, EventReferenceEntity.DATA_PRODUCT)


@router.get(f"{route}/{{id}}/history")
def get_data_product_event_history(
    id: UUID, db: Session = Depends(get_db_session)
) -> GetEventHistoryResponse:
    return GetEventHistoryResponse(
        events=[
            GetEventHistoryResponseItemOld.model_validate(event).convert()
            for event in EventService(db).get_history(
                id, EventReferenceEntity.DATA_PRODUCT
            )
        ]
    )


@router.post(
    f"{old_route}/{{id}}/data_output",
    responses={
        200: {
            "description": "DataOutput successfully created",
            "content": {
                "application/json": {
                    "example": {"id": "random id of the new data_output"}
                }
            },
        },
    },
    dependencies=[
        Depends(
            Authorization.enforce(
                Action.DATA_PRODUCT__CREATE_TECHNICAL_ASSET,
                DataProductResolver,
            )
        )
    ],
    deprecated=True,
)
def create_data_output(
    id: UUID,
    data_output: DataOutputCreate,
    db: Session = Depends(get_db_session),
    authenticated_user: User = Depends(get_authenticated_user),
) -> CreateTechnicalAssetResponse:
    return create_technical_asset(
        id=id,
        technical_asset=data_output,
        db=db,
        authenticated_user=authenticated_user,
    )


@router.post(
    f"{route}/{{id}}/technical_asset",
    responses={
        200: {
            "description": "DataOutput successfully created",
            "content": {
                "application/json": {
                    "example": {"id": "random id of the new data_output"}
                }
            },
        },
    },
    dependencies=[
        Depends(
            Authorization.enforce(
                Action.DATA_PRODUCT__CREATE_TECHNICAL_ASSET,
                DataProductResolver,
            )
        )
    ],
)
def create_technical_asset(
    id: UUID,
    technical_asset: CreateTechnicalAssetRequest,
    db: Session = Depends(get_db_session),
    authenticated_user: User = Depends(get_authenticated_user),
) -> CreateTechnicalAssetResponse:
    technical_asset = DataOutputService(db).create_data_output(id, technical_asset)
    event_id = EventService(db).create_event(
        CreateEvent(
            name=EventType.DATA_OUTPUT_CREATED,
            subject_id=technical_asset.id,
            subject_type=EventReferenceEntity.DATA_OUTPUT,
            target_id=technical_asset.owner_id,
            target_type=EventReferenceEntity.DATA_PRODUCT,
            actor_id=authenticated_user.id,
        ),
    )
    NotificationService(db).create_data_product_notifications(
        data_product_id=technical_asset.owner_id, event_id=event_id
    )
    RefreshInfrastructureLambda().trigger()
    return CreateTechnicalAssetResponse(id=technical_asset.id)


@router.get(
    f"{old_route}/{{id}}/signin_url",
    dependencies=[
        Depends(
            Authorization.enforce(
                Action.DATA_PRODUCT__READ_INTEGRATIONS, DataProductResolver
            )
        ),
    ],
    deprecated=True,
)
def get_signin_url_old(
    id: UUID,
    environment: str,
    db: Session = Depends(get_db_session),
    authenticated_user: User = Depends(get_authenticated_user),
) -> str:
    return get_signin_url(id, environment, db, authenticated_user).signin_url


@router.get(
    f"{route}/{{id}}/signin_url",
    dependencies=[
        Depends(
            Authorization.enforce(
                Action.DATA_PRODUCT__READ_INTEGRATIONS, DataProductResolver
            )
        ),
    ],
)
def get_signin_url(
    id: UUID,
    environment: str,
    db: Session = Depends(get_db_session),
    authenticated_user: User = Depends(get_authenticated_user),
) -> GetSigninUrlResponse:
    return GetSigninUrlResponse(
        signin_url=DataProductService(db).generate_signin_url(
            id, environment, actor=authenticated_user
        )
    )


@router.get(
    f"{old_route}/{{id}}/conveyor_ide_url",
    dependencies=[
        Depends(
            Authorization.enforce(
                Action.DATA_PRODUCT__READ_INTEGRATIONS, DataProductResolver
            )
        ),
    ],
    deprecated=True,
)
def get_conveyor_ide_url_old(id: UUID, db: Session = Depends(get_db_session)) -> str:
    return get_conveyor_ide_url(id=id, db=db).ide_url


@router.get(
    f"{route}/{{id}}/conveyor_ide_url",
    dependencies=[
        Depends(
            Authorization.enforce(
                Action.DATA_PRODUCT__READ_INTEGRATIONS, DataProductResolver
            )
        ),
    ],
)
def get_conveyor_ide_url(
    id: UUID, db: Session = Depends(get_db_session)
) -> GetConveyorIdeUrlResponse:
    return GetConveyorIdeUrlResponse(
        ide_url=DataProductService(db).get_conveyor_ide_url(id)
    )


@router.get(
    f"{old_route}/{{id}}/databricks_workspace_url",
    dependencies=[
        Depends(
            Authorization.enforce(
                Action.DATA_PRODUCT__READ_INTEGRATIONS, DataProductResolver
            )
        ),
    ],
    deprecated=True,
)
def get_databricks_workspace_url_old(
    id: UUID,
    environment: str,
    db: Session = Depends(get_db_session),
) -> str:
    return get_databricks_workspace_url(id, environment, db).databricks_workspace_url


@router.get(
    f"{route}/{{id}}/databricks_workspace_url",
    dependencies=[
        Depends(
            Authorization.enforce(
                Action.DATA_PRODUCT__READ_INTEGRATIONS, DataProductResolver
            )
        ),
    ],
)
def get_databricks_workspace_url(
    id: UUID,
    environment: str,
    db: Session = Depends(get_db_session),
) -> GetDatabricksWorkspaceUrlResponse:
    return GetDatabricksWorkspaceUrlResponse(
        databricks_workspace_url=DataProductService(db).get_databricks_workspace_url(
            id, environment
        )
    )


@router.get(
    f"{old_route}/{{id}}/snowflake_url",
    dependencies=[
        Depends(
            Authorization.enforce(
                Action.DATA_PRODUCT__READ_INTEGRATIONS, DataProductResolver
            )
        ),
    ],
    deprecated=True,
)
def get_snowflake_url_old(
    id: UUID,
    environment: str,
    db: Session = Depends(get_db_session),
) -> str:
    return get_snowflake_url(id, environment, db).snowflake_url


@router.get(
    f"{route}/{{id}}/snowflake_url",
    dependencies=[
        Depends(
            Authorization.enforce(
                Action.DATA_PRODUCT__READ_INTEGRATIONS, DataProductResolver
            )
        ),
    ],
)
def get_snowflake_url(
    id: UUID,
    environment: str,
    db: Session = Depends(get_db_session),
) -> GetSnowflakeUrlResponse:
    return GetSnowflakeUrlResponse(
        snowflake_url=DataProductService(db).get_snowflake_url(id, environment)
    )


@router.get(f"{old_route}/{{id}}/data_outputs", deprecated=True)
def get_data_outputs_old(
    id: UUID, db: Session = Depends(get_db_session)
) -> Sequence[DataOutputGet]:
    return DataProductService(db).get_data_outputs(id)


@router.get(f"{route}/{{id}}/technical_assets")
def get_technical_assets(
    id: UUID, db: Session = Depends(get_db_session)
) -> GetTechnicalAssetsResponse:
    return GetTechnicalAssetsResponse(
        technical_assets=[
            DataOutputGet.model_validate(do).convert()
            for do in get_data_outputs_old(id, db)
        ]
    )


@router.get(
    f"{old_route}/user/{{user_id}}",
    deprecated=True,
    description="**DEPRECATED:** Please use get_data_products with a user filter instead",
)
def get_user_data_products(
    user_id: UUID, db: Session = Depends(get_db_session)
) -> Sequence[DataProductsGet]:
    return DataProductService(db).get_data_products(
        filter_to_user_with_assigment=user_id
    )


@router.get(f"{old_route}/{{id}}", deprecated=True)
def get_data_product_old(
    id: UUID, db: Session = Depends(get_db_session)
) -> DataProductGet:
    return DataProductService(db).get_data_product_old(id)


@router.get(f"{route}/{{id}}")
def get_data_product(
    id: UUID, db: Session = Depends(get_db_session)
) -> GetDataProductResponse:
    return DataProductService(db).get_data_product(id)


@router.get(f"{route}/{{id}}/input_ports")
def get_data_product_input_ports(
    id: UUID,
    db: Session = Depends(get_db_session),
) -> GetDataProductInputPortsResponse:
    return GetDataProductInputPortsResponse(
        input_ports=[
            DatasetLinks.model_validate(input_port).convert()
            for input_port in DataProductService(db).get_input_ports(id)
        ]
    )


@router.get(f"{route}/{{id}}/rolled_up_tags")
def get_data_product_rolled_up_tags(
    id: UUID, db: Session = Depends(get_db_session)
) -> GetDataProductRolledUpTagsResponse:
    return GetDataProductRolledUpTagsResponse(
        rolled_up_tags=DataProductService(db).get_rolled_up_tags(id)
    )


@router.get(
    f"{old_route}/{{id}}/role",
    dependencies=[
        Depends(
            Authorization.enforce(
                Action.DATA_PRODUCT__READ_INTEGRATIONS, DataProductResolver
            )
        ),
    ],
    deprecated=True,
    description="**DEPRECATED:** Please use get_signin_url instead",
)
def get_role(id: UUID, environment: str, db: Session = Depends(get_db_session)) -> str:
    return DataProductService(db).get_data_product_role_arn(id, environment)


@router.delete(
    f"{old_route}/{{id}}/dataset/{{dataset_id}}",
    responses={
        400: {
            "description": "Dataset not found",
            "content": {
                "application/json": {"example": {"detail": "Dataset not found"}}
            },
        },
        404: {
            "description": "Data Product not found",
            "content": {
                "application/json": {"example": {"detail": "Data Product id not found"}}
            },
        },
    },
    dependencies=[
        Depends(
            Authorization.enforce(
                Action.DATA_PRODUCT__REVOKE_OUTPUT_PORT_ACCESS,
                DataProductResolver,
            )
        ),
    ],
    deprecated=True,
)
def unlink_dataset_from_data_product(
    id: UUID,
    dataset_id: UUID,
    db: Session = Depends(get_db_session),
    authenticated_user: User = Depends(get_authenticated_user),
) -> None:
    unlink_input_port_from_data_product(id, dataset_id, db, authenticated_user)


@router.delete(
    f"{route}/{{id}}/input_ports/{{input_port_id}}",
    responses={
        400: {
            "description": "Output port not found",
            "content": {
                "application/json": {"example": {"detail": "Output port not found"}}
            },
        },
        404: {
            "description": "Data Product not found",
            "content": {
                "application/json": {"example": {"detail": "Data Product id not found"}}
            },
        },
    },
    dependencies=[
        Depends(
            Authorization.enforce(
                Action.DATA_PRODUCT__REVOKE_OUTPUT_PORT_ACCESS,
                DataProductResolver,
            )
        ),
    ],
)
def unlink_input_port_from_data_product(
    id: UUID,
    input_port_id: UUID,
    db: Session = Depends(get_db_session),
    authenticated_user: User = Depends(get_authenticated_user),
) -> None:
    data_product_dataset = DataProductService(db).unlink_dataset_from_data_product(
        id, input_port_id
    )

    event_id = EventService(db).create_event(
        CreateEvent(
            name=(
                EventType.DATA_PRODUCT_DATASET_LINK_REMOVED
                if data_product_dataset.status != DecisionStatus.APPROVED
                else EventType.DATA_PRODUCT_DATASET_LINK_DENIED
            ),
            subject_id=id,
            subject_type=EventReferenceEntity.DATA_PRODUCT,
            target_id=data_product_dataset.dataset_id,
            target_type=EventReferenceEntity.DATASET,
            actor_id=authenticated_user.id,
        ),
    )
    if data_product_dataset.status == DecisionStatus.APPROVED:
        NotificationService(db).create_data_product_notifications(
            data_product_id=id, event_id=event_id
        )
    RefreshInfrastructureLambda().trigger()


@router.get(f"{old_route}/{{id}}/data_output/validate_namespace", deprecated=True)
def validate_data_output_namespace(
    id: UUID, namespace: str, db: Session = Depends(get_db_session)
) -> NamespaceValidation:
    return NamespaceValidation(
        validity=DataOutputResourceNameValidator()
        .validate_resource_name(resource_name=namespace, db=db, scope=id)
        .validity
    )
