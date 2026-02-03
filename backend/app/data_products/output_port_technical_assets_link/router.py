from copy import deepcopy
from typing import Sequence
from uuid import UUID

from fastapi import APIRouter, BackgroundTasks, Depends
from sqlalchemy.orm import Session

from app.authorization.role_assignments.output_port.service import RoleAssignmentService
from app.core.auth.auth import get_authenticated_user
from app.core.authz import Action, Authorization, DataOutputDatasetAssociationResolver
from app.core.authz.resolvers import DataOutputResolver, DatasetResolver
from app.core.aws.refresh_infrastructure_lambda import RefreshInfrastructureLambda
from app.data_products.output_port_technical_assets_link.schema_request import (
    ApproveLinkBetweenTechnicalAssetAndOutputPortRequest,
    DenyLinkBetweenTechnicalAssetAndOutputPortRequest,
    LinkTechnicalAssetToOutputPortRequest,
    UnLinkTechnicalAssetToOutputPortRequest,
)
from app.data_products.output_port_technical_assets_link.schema_response import (
    LinkTechnicalAssetsToOutputPortResponse,
)
from app.data_products.output_port_technical_assets_link.service import (
    DataOutputDatasetService,
)
from app.data_products.technical_assets import email
from app.data_products.technical_assets.service import DataOutputService
from app.database.database import get_db_session
from app.events.enums import EventReferenceEntity, EventType
from app.events.schema import CreateEvent
from app.events.service import EventService
from app.pending_actions.schema import DataOutputDatasetPendingAction
from app.users.notifications.service import NotificationService
from app.users.schema import User

router = APIRouter(tags=["Data Products - Technical assets"])

old_route = "/data_output_dataset_links"
route = (
    "/v2/data_products/{data_product_id}/output_ports/{output_port_id}/technical_assets"
)


@router.post(
    f"{old_route}/approve/{{id}}",
    dependencies=[
        Depends(
            Authorization.enforce(
                Action.OUTPUT_PORT__APPROVE_TECHNICAL_ASSET_LINK_REQUEST,
                DataOutputDatasetAssociationResolver,
            )
        )
    ],
    deprecated=True,
)
def approve_data_output_link(
    id: UUID,
    db: Session = Depends(get_db_session),
    authenticated_user: User = Depends(get_authenticated_user),
) -> None:
    link = DataOutputDatasetService(db).get_link_by_id(
        id,
    )
    approve_output_port_technical_asset_link(
        data_product_id=link.dataset.data_product_id,
        output_port_id=link.dataset_id,
        request=ApproveLinkBetweenTechnicalAssetAndOutputPortRequest(
            technical_asset_id=link.data_output_id
        ),
        db=db,
        authenticated_user=authenticated_user,
    )


@router.post(
    f"{route}/approve_link_request",
    dependencies=[
        Depends(
            Authorization.enforce(
                Action.OUTPUT_PORT__APPROVE_TECHNICAL_ASSET_LINK_REQUEST,
                DatasetResolver,
                object_id="output_port_id",
            )
        )
    ],
)
def approve_output_port_technical_asset_link(
    data_product_id: UUID,
    output_port_id: UUID,
    request: ApproveLinkBetweenTechnicalAssetAndOutputPortRequest,
    db: Session = Depends(get_db_session),
    authenticated_user: User = Depends(get_authenticated_user),
):
    output_link = DataOutputDatasetService(db).approve_data_output_link(
        data_product_id=data_product_id,
        technical_asset_id=request.technical_asset_id,
        output_port_id=output_port_id,
        actor=authenticated_user,
    )

    event_id = EventService(db).create_event(
        CreateEvent(
            name=EventType.DATA_OUTPUT_DATASET_LINK_APPROVED,
            subject_id=output_link.dataset_id,
            subject_type=EventReferenceEntity.DATASET,
            target_id=output_link.data_output_id,
            target_type=EventReferenceEntity.DATA_OUTPUT,
            actor_id=authenticated_user.id,
        ),
    )
    NotificationService(db).create_dataset_notifications(
        dataset_id=output_link.dataset_id,
        event_id=event_id,
        extra_receiver_ids=[output_link.requested_by_id],
    )
    RefreshInfrastructureLambda().trigger()


@router.post(
    f"{old_route}/deny/{{id}}",
    dependencies=[
        Depends(
            Authorization.enforce(
                Action.OUTPUT_PORT__APPROVE_TECHNICAL_ASSET_LINK_REQUEST,
                DataOutputDatasetAssociationResolver,
            )
        )
    ],
    deprecated=True,
)
def deny_data_output_link(
    id: UUID,
    db: Session = Depends(get_db_session),
    authenticated_user: User = Depends(get_authenticated_user),
) -> None:
    link = DataOutputDatasetService(db).get_link_by_id(id)
    deny_output_port_technical_asset_link(
        data_product_id=link.dataset.data_product_id,
        output_port_id=link.dataset_id,
        request=DenyLinkBetweenTechnicalAssetAndOutputPortRequest(
            technical_asset_id=link.data_output_id
        ),
        db=db,
        authenticated_user=authenticated_user,
    )


@router.post(
    f"{route}/deny_link_request",
    dependencies=[
        Depends(
            Authorization.enforce(
                Action.OUTPUT_PORT__APPROVE_TECHNICAL_ASSET_LINK_REQUEST,
                DatasetResolver,
                object_id="output_port_id",
            )
        )
    ],
)
def deny_output_port_technical_asset_link(
    data_product_id: UUID,
    output_port_id: UUID,
    request: DenyLinkBetweenTechnicalAssetAndOutputPortRequest,
    db: Session = Depends(get_db_session),
    authenticated_user: User = Depends(get_authenticated_user),
) -> None:
    output_link = DataOutputDatasetService(db).deny_data_output_link(
        data_product_id=data_product_id,
        technical_asset_id=request.technical_asset_id,
        output_port_id=output_port_id,
        actor=authenticated_user,
    )

    event_id = EventService(db).create_event(
        CreateEvent(
            name=EventType.DATA_OUTPUT_DATASET_LINK_DENIED,
            subject_id=output_link.dataset_id,
            subject_type=EventReferenceEntity.DATASET,
            target_id=output_link.data_output_id,
            target_type=EventReferenceEntity.DATA_OUTPUT,
            actor_id=authenticated_user.id,
        ),
    )
    NotificationService(db).create_dataset_notifications(
        dataset_id=output_link.dataset_id,
        event_id=event_id,
        extra_receiver_ids=[output_link.requested_by_id],
    )


@router.post(
    f"{old_route}/remove/{{id}}",
    dependencies=[
        Depends(
            Authorization.enforce(
                Action.OUTPUT_PORT__REVOKE_TECHNICAL_ASSET_LINK,
                DataOutputDatasetAssociationResolver,
            )
        )
    ],
    deprecated=True,
    description="**DEPRECATED:** Please use unlink_output_port_from_technical_asset instead",
)
def remove_data_output_link(
    id: UUID,
    db: Session = Depends(get_db_session),
    authenticated_user: User = Depends(get_authenticated_user),
) -> None:
    output_link = DataOutputDatasetService(db).get_link_by_id(
        id,
    )
    unlink_output_port_from_technical_asset(
        output_link.dataset.data_product_id,
        output_link.dataset_id,
        UnLinkTechnicalAssetToOutputPortRequest(
            technical_asset_id=output_link.data_output_id
        ),
        db,
        authenticated_user,
    )


@router.get(
    f"{old_route}/actions",
    deprecated=True,
    description="**DEPRECATED:** Please use get user actions globally instead",
)
def get_user_pending_actions(
    db: Session = Depends(get_db_session),
    authenticated_user: User = Depends(get_authenticated_user),
) -> Sequence[DataOutputDatasetPendingAction]:
    return DataOutputDatasetService(db).get_user_pending_actions(authenticated_user)


@router.post(
    f"{route}/add",
    responses={
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
                Action.DATA_PRODUCT__REQUEST_TECHNICAL_ASSET_LINK,
                DataOutputResolver,
            )
        ),
    ],
)
def link_output_port_to_technical_asset(
    data_product_id: UUID,
    output_port_id: UUID,
    request: LinkTechnicalAssetToOutputPortRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db_session),
    authenticated_user: User = Depends(get_authenticated_user),
) -> LinkTechnicalAssetsToOutputPortResponse:
    dataset_link = DataOutputService(db).link_dataset_to_data_output(
        data_product_id,
        request.technical_asset_id,
        output_port_id,
        actor=authenticated_user,
    )

    EventService(db).create_event(
        CreateEvent(
            name=EventType.DATA_OUTPUT_DATASET_LINK_REQUESTED,
            subject_id=request.technical_asset_id,
            subject_type=EventReferenceEntity.DATA_OUTPUT,
            target_id=output_port_id,
            target_type=EventReferenceEntity.DATASET,
            actor_id=authenticated_user.id,
        ),
    )
    RefreshInfrastructureLambda().trigger()

    approvers = RoleAssignmentService(db).users_with_authz_action(
        dataset_link.dataset_id,
        Action.OUTPUT_PORT__APPROVE_TECHNICAL_ASSET_LINK_REQUEST,
    )
    if authenticated_user not in approvers:
        background_tasks.add_task(
            email.send_link_dataset_email(
                dataset_link.dataset,
                dataset_link.data_output,
                requester=deepcopy(authenticated_user),
                approvers=[deepcopy(approver) for approver in approvers],
            )
        )
    return LinkTechnicalAssetsToOutputPortResponse(link_id=dataset_link.id)


@router.delete(
    f"{route}/remove",
    responses={
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
                DataOutputResolver,
            )
        ),
    ],
)
def unlink_output_port_from_technical_asset(
    data_product_id: UUID,
    output_port_id: UUID,
    request: UnLinkTechnicalAssetToOutputPortRequest,
    db: Session = Depends(get_db_session),
    authenticated_user: User = Depends(get_authenticated_user),
) -> None:
    data_output = DataOutputService(db).unlink_dataset_from_data_output(
        data_product_id=data_product_id,
        id=request.technical_asset_id,
        dataset_id=output_port_id,
    )

    event_id = EventService(db).create_event(
        CreateEvent(
            name=EventType.DATA_OUTPUT_DATASET_LINK_REMOVED,
            subject_id=request.technical_asset_id,
            subject_type=EventReferenceEntity.DATA_OUTPUT,
            target_id=output_port_id,
            target_type=EventReferenceEntity.DATASET,
            actor_id=authenticated_user.id,
        ),
    )
    NotificationService(db).create_data_product_notifications(
        data_product_id=data_output.owner_id, event_id=event_id
    )
    RefreshInfrastructureLambda().trigger()
