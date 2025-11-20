from copy import deepcopy
from typing import Optional, Sequence
from uuid import UUID

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.auth.auth import get_authenticated_user
from app.core.authz import Action, Authorization, DataProductResolver
from app.core.authz.resolvers import EmptyResolver
from app.core.aws.refresh_infrastructure_lambda import RefreshInfrastructureLambda
from app.core.namespace.validation import (
    NamespaceLengthLimits,
    NamespaceSuggestion,
    NamespaceValidation,
)
from app.data_outputs.schema_request import DataOutputCreate
from app.data_outputs.schema_response import DataOutputGet, TechnicalAssetsGet
from app.data_outputs.service import DataOutputService
from app.data_product_settings.service import DataProductSettingService
from app.data_products import email
from app.data_products.schema_request import (
    DataProductAboutUpdate,
    DataProductCreate,
    DataProductStatusUpdate,
    DataProductUpdate,
    DataProductURLType,
    DataProductUsageUpdate,
    LinkDatasetsToDataProduct,
)
from app.data_products.schema_response import (
    DataProductGet,
    DataProductsGet,
    DataProductsGetItem,
    LinkDatasetsToDataProductPost,
)
from app.data_products.service import DataProductService
from app.data_products_datasets.model import DataProductDatasetAssociation
from app.database.database import get_db_session
from app.datasets.enums import DatasetAccessType
from app.events.enums import EventReferenceEntity, EventType
from app.events.schema import CreateEvent
from app.events.schema_response import EventGet, EventsGet
from app.events.service import EventService
from app.graph.graph import Graph
from app.notifications.service import NotificationService
from app.role_assignments.data_product.auth import DataProductAuthAssignment
from app.role_assignments.data_product.schema import (
    CreateRoleAssignment,
    UpdateRoleAssignment,
)
from app.role_assignments.data_product.service import RoleAssignmentService
from app.role_assignments.dataset.service import (
    RoleAssignmentService as DatasetRoleAssignmentService,
)
from app.role_assignments.enums import DecisionStatus
from app.roles.schema import Prototype, Scope
from app.roles.service import RoleService
from app.users.schema import User

router = APIRouter(tags=["data_products"])


# Use get_data_products, with user_id filter instead
@router.get(
    "/user/{user_id}",
    deprecated=True,
)
def get_user_data_products(
    user_id: UUID,
    db: Session = Depends(get_db_session),
) -> Sequence[DataProductsGet]:
    return get_data_products(db, user_id=user_id)


@router.get("/{id}")
def get_data_product(id: UUID, db: Session = Depends(get_db_session)) -> DataProductGet:
    return DataProductService(db).get_data_product(id)


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
) -> dict[str, UUID]:
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
    return {"id": created_data_product.id}


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
            CreateRoleAssignment(
                user_id=owner_id,
                role_id=owner_role.id,
            ),
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
) -> dict[str, UUID]:
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
        if dataset_link.dataset.access_type != DatasetAccessType.PUBLIC:
            approvers = DatasetRoleAssignmentService(db).users_with_authz_action(
                dataset_link.dataset_id,
                Action.DATASET__APPROVE_DATAPRODUCT_ACCESS_REQUEST,
            )
            background_tasks.add_task(
                email.send_dataset_link_email(
                    dataset_link.data_product,
                    dataset_link.dataset,
                    requester=deepcopy(actor),
                    approvers=[deepcopy(approver) for approver in approvers],
                )
            )


@router.get(
    "/{id}/role",
    dependencies=[
        Depends(
            Authorization.enforce(
                Action.DATA_PRODUCT__READ_INTEGRATIONS, DataProductResolver
            )
        ),
    ],
)
def get_role(id: UUID, environment: str, db: Session = Depends(get_db_session)) -> str:
    return DataProductService(db).get_data_product_role_arn(id, environment)


@router.get("/{id}/graph")
def get_graph_data(
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
router = APIRouter()

old_data_product_route = "/data_products"
data_product_route = "/v2/data_products"
router.include_router(_router, prefix=old_data_product_route, deprecated=True)
router.include_router(_router, prefix=data_product_route)


@router.get(
    f"{old_data_product_route}/namespace_suggestion",
    tags=["data_products"],
    deprecated=True,
)
def get_data_product_namespace_suggestion(name: str) -> NamespaceSuggestion:
    return DataProductService.data_product_namespace_suggestion(name)


@router.get(
    f"{old_data_product_route}/validate_namespace",
    tags=["data_products"],
    deprecated=True,
)
def validate_data_product_namespace(
    namespace: str, db: Session = Depends(get_db_session)
) -> NamespaceValidation:
    return DataProductService(db).validate_data_product_namespace(namespace)


@router.get(
    f"{old_data_product_route}/namespace_length_limits",
    tags=["data_products"],
    deprecated=True,
)
def get_data_product_namespace_length_limits() -> NamespaceLengthLimits:
    return DataProductService.data_product_namespace_length_limits()


@router.get(
    f"{old_data_product_route}/{{id}}/signin_url",
    dependencies=[
        Depends(
            Authorization.enforce(
                Action.DATA_PRODUCT__READ_INTEGRATIONS, DataProductResolver
            )
        ),
    ],
    tags=["data_products"],
    deprecated=True,
)
def get_signin_url(
    id: UUID,
    environment: str,
    db: Session = Depends(get_db_session),
    authenticated_user: User = Depends(get_authenticated_user),
) -> str:
    return get_data_product_url(
        id,
        environment,
        url_type=DataProductURLType.SIGN_IN,
        db=db,
        authenticated_user=authenticated_user,
    )


@router.get(
    f"{old_data_product_route}/{{id}}/conveyor_ide_url",
    dependencies=[
        Depends(
            Authorization.enforce(
                Action.DATA_PRODUCT__READ_INTEGRATIONS, DataProductResolver
            )
        ),
    ],
    tags=["data_products"],
    deprecated=True,
)
def get_conveyor_ide_url(
    id: UUID,
    db: Session = Depends(get_db_session),
    authenticated_user: User = Depends(get_authenticated_user),
) -> str:
    return get_data_product_url(
        id,
        "random",
        url_type=DataProductURLType.DATABRICKS,
        db=db,
        authenticated_user=authenticated_user,
    )


@router.get(
    f"{old_data_product_route}/{{id}}/databricks_workspace_url",
    dependencies=[
        Depends(
            Authorization.enforce(
                Action.DATA_PRODUCT__READ_INTEGRATIONS, DataProductResolver
            )
        ),
    ],
    tags=["data_products"],
    deprecated=True,
)
def get_databricks_workspace_url(
    id: UUID,
    environment: str,
    db: Session = Depends(get_db_session),
    authenticated_user: User = Depends(get_authenticated_user),
) -> str:
    return get_data_product_url(
        id,
        environment,
        url_type=DataProductURLType.DATABRICKS,
        db=db,
        authenticated_user=authenticated_user,
    )


@router.get(
    f"{data_product_route}/{{id}}/url",
    dependencies=[
        Depends(
            Authorization.enforce(
                Action.DATA_PRODUCT__READ_INTEGRATIONS, DataProductResolver
            )
        ),
    ],
    tags=["data_products"],
)
def get_data_product_url(
    id: UUID,
    environment: str,
    url_type: DataProductURLType,
    db: Session = Depends(get_db_session),
    authenticated_user: User = Depends(get_authenticated_user),
) -> str:

    match url_type:
        case DataProductURLType.DATABRICKS:
            return DataProductService(db).get_databricks_workspace_url(id, environment)
        case DataProductURLType.SNOWFLAKE:
            return DataProductService(db).get_snowflake_url(id, environment)
        case DataProductURLType.CONVEYOR:
            # TODO no environment here
            return DataProductService(db).get_conveyor_ide_url(id)
        case DataProductURLType.SIGN_IN:
            return DataProductService(db).generate_signin_url(
                id, environment, actor=authenticated_user
            )
        case _:
            raise HTTPException(status_code=400, detail="Invalid url_type provided")


@router.get(
    f"{old_data_product_route}/{{id}}/snowflake_url",
    dependencies=[
        Depends(
            Authorization.enforce(
                Action.DATA_PRODUCT__READ_INTEGRATIONS, DataProductResolver
            )
        ),
    ],
    tags=["data_products"],
    deprecated=True,
)
def get_snowflake_url(
    id: UUID,
    environment: str,
    db: Session = Depends(get_db_session),
    authenticated_user: User = Depends(get_authenticated_user),
) -> str:
    return get_data_product_url(
        id,
        environment,
        url_type=DataProductURLType.SNOWFLAKE,
        db=db,
        authenticated_user=authenticated_user,
    )


@router.post(
    f"{data_product_route}/{{id}}/input_ports",
    responses={
        400: {
            "description": "Port not found",
            "content": {"application/json": {"example": {"detail": "Port not found"}}},
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
                Action.DATA_PRODUCT__REQUEST_DATASET_ACCESS,
                DataProductResolver,
            )
        ),
    ],
    tags=["data_products"],
)
def link_input_ports_to_data_product(
    id: UUID,
    link_datasets: LinkDatasetsToDataProduct,
    background_tasks: BackgroundTasks,
    authenticated_user: User = Depends(get_authenticated_user),
    db: Session = Depends(get_db_session),
) -> LinkDatasetsToDataProductPost:
    dataset_links = DataProductService(db).link_datasets_to_data_product(
        id,
        link_datasets.dataset_ids,
        link_datasets.justification,
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
    return LinkDatasetsToDataProductPost(
        dataset_links=[dataset_link.id for dataset_link in dataset_links]
    )


@router.post(
    f"{old_data_product_route}/{{id}}/link_datasets",
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
                Action.DATA_PRODUCT__REQUEST_DATASET_ACCESS,
                DataProductResolver,
            )
        ),
    ],
    tags=["data_products"],
    deprecated=True,
)
def link_datasets_to_data_product(
    id: UUID,
    link_datasets: LinkDatasetsToDataProduct,
    background_tasks: BackgroundTasks,
    authenticated_user: User = Depends(get_authenticated_user),
    db: Session = Depends(get_db_session),
) -> LinkDatasetsToDataProductPost:
    return link_input_ports_to_data_product(
        id, link_datasets, background_tasks, authenticated_user, db
    )


@router.delete(
    f"{data_product_route}/{{id}}/input_ports/{{input_port_id}}",
    responses={
        400: {
            "description": "Input port not found",
            "content": {
                "application/json": {"example": {"detail": "Input port not found"}}
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
                Action.DATA_PRODUCT__REVOKE_DATASET_ACCESS,
                DataProductResolver,
            )
        ),
    ],
    tags=["data_products"],
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


@router.delete(
    f"{old_data_product_route}/{{id}}/dataset/{{dataset_id}}",
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
                Action.DATA_PRODUCT__REVOKE_DATASET_ACCESS,
                DataProductResolver,
            )
        ),
    ],
    tags=["data_products"],
    deprecated=True,
)
def unlink_dataset_from_data_product(
    id: UUID,
    dataset_id: UUID,
    db: Session = Depends(get_db_session),
    authenticated_user: User = Depends(get_authenticated_user),
) -> None:
    return unlink_input_port_from_data_product(id, dataset_id, db, authenticated_user)


@router.get(
    f"{data_product_route}/{{id}}/technical_assets",
    tags=["data_products"],
)
def get_technical_assets(
    id: UUID,
    db: Session = Depends(get_db_session),
) -> TechnicalAssetsGet:
    return DataProductService(db).get_data_outputs(id)


@router.get(
    f"{old_data_product_route}/{{id}}/data_outputs",
    deprecated=True,
    tags=["data_products"],
)
def get_data_outputs(
    id: UUID,
    db: Session = Depends(get_db_session),
) -> Sequence[DataOutputGet]:
    return get_technical_assets(id, db)


@router.post(
    f"{data_product_route}/{{id}}/technical_assets",
    responses={
        200: {
            "description": "Technical asset successfully created",
            "content": {
                "application/json": {
                    "example": {"id": "random id of the new technical asset"}
                }
            },
        },
    },
    dependencies=[
        Depends(
            Authorization.enforce(
                Action.DATA_PRODUCT__CREATE_DATA_OUTPUT,
                DataProductResolver,
            )
        )
    ],
    tags=["data_products"],
)
def create_technical_asset(
    id: UUID,
    technical_asset: DataOutputCreate,
    db: Session = Depends(get_db_session),
    authenticated_user: User = Depends(get_authenticated_user),
) -> dict[str, UUID]:
    data_output = DataOutputService(db).create_data_output(id, technical_asset)
    event_id = EventService(db).create_event(
        CreateEvent(
            name=EventType.DATA_OUTPUT_CREATED,
            subject_id=data_output.id,
            subject_type=EventReferenceEntity.DATA_OUTPUT,
            target_id=data_output.owner_id,
            target_type=EventReferenceEntity.DATA_PRODUCT,
            actor_id=authenticated_user.id,
        ),
    )
    NotificationService(db).create_data_product_notifications(
        data_product_id=data_output.owner_id, event_id=event_id
    )
    RefreshInfrastructureLambda().trigger()
    return {"id": data_output.id}


@router.post(
    f"{old_data_product_route}/{{id}}/data_output",
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
                Action.DATA_PRODUCT__CREATE_DATA_OUTPUT,
                DataProductResolver,
            )
        )
    ],
    deprecated=True,
    tags=["data_products"],
)
def create_data_output(
    id: UUID,
    data_output: DataOutputCreate,
    db: Session = Depends(get_db_session),
    authenticated_user: User = Depends(get_authenticated_user),
) -> dict[str, UUID]:
    return create_technical_asset(id, data_output, db, authenticated_user)


@router.get(
    f"{old_data_product_route}/{{id}}/data_output/validate_namespace",
    deprecated=True,
    tags=["data_products"],
)
async def validate_data_output_namespace(
    id: UUID, namespace: str, db: Session = Depends(get_db_session)
) -> NamespaceValidation:
    return DataProductService(db).validate_data_output_namespace(namespace, id)


@router.get(old_data_product_route, deprecated=True, tags=["data_products"])
def get_data_products(
    db: Session = Depends(get_db_session),
    user_id: Optional[UUID] = None,
) -> Sequence[DataProductsGetItem]:
    return DataProductService(db).get_data_products(user_id)


@router.get(data_product_route, tags=["data_products"])
def get_data_products(
    db: Session = Depends(get_db_session),
    user_id: Optional[UUID] = None,
) -> DataProductsGet:
    return DataProductsGet(
        data_products=DataProductService(db).get_data_products(user_id)
    )


@router.get(
    f"{old_data_product_route}/{{id}}/history", deprecated=True, tags=["data_products"]
)
def get_event_history(
    id: UUID, db: Session = Depends(get_db_session)
) -> Sequence[EventGet]:
    return EventService(db).get_history(id, EventReferenceEntity.DATA_PRODUCT)


@router.get(f"{data_product_route}/{{id}}/history", tags=["data_products"])
def get_event_history(id: UUID, db: Session = Depends(get_db_session)) -> EventsGet:
    return EventsGet(
        events=EventService(db).get_history(id, EventReferenceEntity.DATA_PRODUCT)
    )
