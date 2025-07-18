from typing import Sequence
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
from app.data_outputs.schema_response import DataOutputGet
from app.data_outputs.service import DataOutputService
from app.data_product_settings.service import DataProductSettingService
from app.data_products import email
from app.data_products.schema_request import (
    DataProductAboutUpdate,
    DataProductCreate,
    DataProductStatusUpdate,
    DataProductUpdate,
)
from app.data_products.schema_response import DataProductGet, DataProductsGet
from app.data_products.service import DataProductService
from app.data_products_datasets.model import DataProductDatasetAssociation
from app.database.database import get_db_session
from app.datasets.enums import DatasetAccessType
from app.events.enums import EventReferenceEntity, EventType
from app.events.schema import CreateEvent
from app.events.schema_response import EventGet
from app.events.service import EventService
from app.graph.graph import Graph
from app.notifications.service import NotificationService
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

router = APIRouter(prefix="/data_products", tags=["data_products"])


@router.get("")
def get_data_products(
    db: Session = Depends(get_db_session),
) -> Sequence[DataProductsGet]:
    return DataProductService(db).get_data_products()


@router.get("/namespace_suggestion")
def get_data_product_namespace_suggestion(name: str) -> NamespaceSuggestion:
    return DataProductService.data_product_namespace_suggestion(name)


@router.get("/validate_namespace")
def validate_data_product_namespace(
    namespace: str, db: Session = Depends(get_db_session)
) -> NamespaceValidation:
    return DataProductService(db).validate_data_product_namespace(namespace)


@router.get("/namespace_length_limits")
def get_data_product_namespace_length_limits() -> NamespaceLengthLimits:
    return DataProductService.data_product_namespace_length_limits()


@router.get("/user/{user_id}")
def get_user_data_products(
    user_id: UUID, db: Session = Depends(get_db_session)
) -> Sequence[DataProductsGet]:
    return DataProductService(db).get_user_data_products(user_id)


@router.get("/{id}")
def get_data_product(id: UUID, db: Session = Depends(get_db_session)) -> DataProductGet:
    return DataProductService(db).get_data_product(id)


@router.get("/{id}/history")
def get_event_history(
    id: UUID, db: Session = Depends(get_db_session)
) -> Sequence[EventGet]:
    return EventService(db).get_history(id, EventReferenceEntity.DATA_PRODUCT)


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
        assignment_service.update_assignment(
            UpdateRoleAssignment(id=response.id, decision=DecisionStatus.APPROVED),
            actor=actor,
        )
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


@router.post(
    "/{id}/data_output",
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
)
def create_data_output(
    id: UUID,
    data_output: DataOutputCreate,
    db: Session = Depends(get_db_session),
    authenticated_user: User = Depends(get_authenticated_user),
) -> dict[str, UUID]:
    data_output = DataOutputService(db).create_data_output(id, data_output)
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


@router.get("/{id}/data_output/validate_namespace")
async def validate_data_output_namespace(
    id: UUID, namespace: str, db: Session = Depends(get_db_session)
) -> NamespaceValidation:
    return DataProductService(db).validate_data_output_namespace(namespace, id)


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


@router.post(
    "/{id}/dataset/{dataset_id}",
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
)
def link_dataset_to_data_product(
    id: UUID,
    dataset_id: UUID,
    background_tasks: BackgroundTasks,
    authenticated_user: User = Depends(get_authenticated_user),
    db: Session = Depends(get_db_session),
) -> dict[str, UUID]:
    dataset_link = DataProductService(db).link_dataset_to_data_product(
        id, dataset_id, actor=authenticated_user
    )

    event_id = EventService(db).create_event(
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
        ),
    )
    if dataset_link.status == DecisionStatus.APPROVED:
        NotificationService(db).create_data_product_notifications(
            data_product_id=dataset_link.data_product_id, event_id=event_id
        )

    _send_dataset_link_emails(dataset_link, background_tasks, authenticated_user, db)
    RefreshInfrastructureLambda().trigger()
    return {"id": dataset_link.id}


def _send_dataset_link_emails(
    dataset_link: DataProductDatasetAssociation,
    background_tasks: BackgroundTasks,
    actor: User,
    db: Session,
) -> None:
    if dataset_link.dataset.access_type != DatasetAccessType.PUBLIC:
        approvers = DatasetRoleAssignmentService(db).users_with_authz_action(
            dataset_link.dataset_id, Action.DATASET__APPROVE_DATAPRODUCT_ACCESS_REQUEST
        )
        background_tasks.add_task(
            email.send_dataset_link_email(
                dataset_link.data_product,
                dataset_link.dataset,
                requester=actor,
                approvers=approvers,
            )
        )


@router.delete(
    "/{id}/dataset/{dataset_id}",
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
)
def unlink_dataset_from_data_product(
    id: UUID,
    dataset_id: UUID,
    db: Session = Depends(get_db_session),
    authenticated_user: User = Depends(get_authenticated_user),
) -> None:
    data_product_dataset = DataProductService(db).unlink_dataset_from_data_product(
        id, dataset_id
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


@router.get(
    "/{id}/signin_url",
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
) -> str:
    return DataProductService(db).generate_signin_url(
        id, environment, actor=authenticated_user
    )


@router.get(
    "/{id}/conveyor_ide_url",
    dependencies=[
        Depends(
            Authorization.enforce(
                Action.DATA_PRODUCT__READ_INTEGRATIONS, DataProductResolver
            )
        ),
    ],
)
def get_conveyor_ide_url(id: UUID, db: Session = Depends(get_db_session)) -> str:
    return DataProductService(db).get_conveyor_ide_url(id)


@router.get(
    "/{id}/databricks_workspace_url",
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
) -> str:
    return DataProductService(db).get_databricks_workspace_url(id, environment)


@router.get(
    "/{id}/snowflake_url",
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
) -> str:
    return DataProductService(db).get_snowflake_url(id, environment)


@router.get("/{id}/data_outputs")
def get_data_outputs(
    id: UUID, db: Session = Depends(get_db_session)
) -> Sequence[DataOutputGet]:
    return DataProductService(db).get_data_outputs(id)


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
) -> None:
    return DataProductSettingService(db).set_value_for_product(setting_id, id, value)
