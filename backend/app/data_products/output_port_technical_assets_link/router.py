from copy import deepcopy
from uuid import UUID

from fastapi import APIRouter, BackgroundTasks, Depends, Request
from sqlalchemy.orm import Session

from app.authorization.role_assignments.output_port.service import RoleAssignmentService
from app.core.auth.auth import get_authenticated_user
from app.core.authz import Action, Authorization
from app.core.authz.resolvers import (
    DataProductResolver,
    DatasetResolver,
)
from app.core.aws.refresh_infrastructure_lambda import RefreshInfrastructureLambda
from app.core.webhooks.v2 import emit_event_after
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
from app.data_products.schema_response import GetDataProductResponse
from app.data_products.service import DataProductService
from app.data_products.technical_assets import email
from app.data_products.technical_assets.schema_response import DataOutputGet
from app.data_products.technical_assets.service import DataOutputService
from app.database.database import get_db_session
from app.events.enums import EventReferenceEntity, EventType
from app.events.schema import CreateEvent
from app.events.service import EventService
from app.users.notifications.service import NotificationService
from app.users.schema import User

_emit_technical_asset_linked = emit_event_after(
    "technical_asset.linked",
    lambda request, data_product_id, db, **_: {
        "data_product": GetDataProductResponse.model_validate(
            DataProductService(db).get_data_product(data_product_id)
        ),
        "technical_asset": DataOutputGet.model_validate(
            DataOutputService(db).get_data_output(
                data_product_id, request.state.technical_asset_id
            )
        ).convert(),
    },
)
_emit_technical_asset_link_approved = emit_event_after(
    "technical_asset.link_approved",
    lambda request, data_product_id, db, **_: {
        "data_product": GetDataProductResponse.model_validate(
            DataProductService(db).get_data_product(data_product_id)
        ),
        "technical_asset": DataOutputGet.model_validate(
            DataOutputService(db).get_data_output(
                data_product_id, request.state.technical_asset_id
            )
        ).convert(),
    },
)
_emit_technical_asset_link_denied = emit_event_after(
    "technical_asset.link_denied",
    lambda request, data_product_id, db, **_: {
        "data_product": GetDataProductResponse.model_validate(
            DataProductService(db).get_data_product(data_product_id)
        ),
        "technical_asset": DataOutputGet.model_validate(
            DataOutputService(db).get_data_output(
                data_product_id, request.state.technical_asset_id
            )
        ).convert(),
    },
)
_emit_technical_asset_unlinked = emit_event_after(
    "technical_asset.unlinked",
    lambda request, data_product_id, db, **_: {
        "data_product": GetDataProductResponse.model_validate(
            DataProductService(db).get_data_product(data_product_id)
        ),
        "technical_asset": DataOutputGet.model_validate(
            DataOutputService(db).get_data_output(
                data_product_id, request.state.technical_asset_id
            )
        ).convert(),
    },
)

router = APIRouter(tags=["Data Products - Technical assets"])

route = (
    "/v2/data_products/{data_product_id}/output_ports/{output_port_id}/technical_assets"
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
        ),
        Depends(_emit_technical_asset_link_approved),
    ],
)
def approve_output_port_technical_asset_link(
    data_product_id: UUID,
    output_port_id: UUID,
    link_request: ApproveLinkBetweenTechnicalAssetAndOutputPortRequest,
    request: Request,
    db: Session = Depends(get_db_session),
    authenticated_user: User = Depends(get_authenticated_user),
):
    output_link = DataOutputDatasetService(db).approve_data_output_link(
        data_product_id=data_product_id,
        technical_asset_id=link_request.technical_asset_id,
        output_port_id=output_port_id,
        actor=authenticated_user,
    )
    request.state.technical_asset_id = output_link.data_output_id

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
    f"{route}/deny_link_request",
    dependencies=[
        Depends(
            Authorization.enforce(
                Action.OUTPUT_PORT__APPROVE_TECHNICAL_ASSET_LINK_REQUEST,
                DatasetResolver,
                object_id="output_port_id",
            )
        ),
        Depends(_emit_technical_asset_link_denied),
    ],
)
def deny_output_port_technical_asset_link(
    data_product_id: UUID,
    output_port_id: UUID,
    link_request: DenyLinkBetweenTechnicalAssetAndOutputPortRequest,
    request: Request,
    db: Session = Depends(get_db_session),
    authenticated_user: User = Depends(get_authenticated_user),
) -> None:
    output_link = DataOutputDatasetService(db).deny_data_output_link(
        data_product_id=data_product_id,
        technical_asset_id=link_request.technical_asset_id,
        output_port_id=output_port_id,
        actor=authenticated_user,
    )
    request.state.technical_asset_id = output_link.data_output_id

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
                DataProductResolver,
                object_id="data_product_id",
            )
        ),
        Depends(_emit_technical_asset_linked),
    ],
)
def link_output_port_to_technical_asset(
    data_product_id: UUID,
    output_port_id: UUID,
    link_request: LinkTechnicalAssetToOutputPortRequest,
    request: Request,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db_session),
    authenticated_user: User = Depends(get_authenticated_user),
) -> LinkTechnicalAssetsToOutputPortResponse:
    dataset_link = DataOutputService(db).link_dataset_to_data_output(
        data_product_id,
        link_request.technical_asset_id,
        output_port_id,
        actor=authenticated_user,
    )
    request.state.technical_asset_id = dataset_link.data_output_id

    EventService(db).create_event(
        CreateEvent(
            name=EventType.DATA_OUTPUT_DATASET_LINK_REQUESTED,
            subject_id=link_request.technical_asset_id,
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
                DataProductResolver,
                object_id="data_product_id",
            )
        ),
        Depends(_emit_technical_asset_unlinked),
    ],
)
def unlink_output_port_from_technical_asset(
    data_product_id: UUID,
    output_port_id: UUID,
    link_request: UnLinkTechnicalAssetToOutputPortRequest,
    request: Request,
    db: Session = Depends(get_db_session),
    authenticated_user: User = Depends(get_authenticated_user),
) -> None:
    data_output = DataOutputService(db).unlink_dataset_from_data_output(
        data_product_id=data_product_id,
        id=link_request.technical_asset_id,
        dataset_id=output_port_id,
    )
    request.state.technical_asset_id = data_output.id

    event_id = EventService(db).create_event(
        CreateEvent(
            name=EventType.DATA_OUTPUT_DATASET_LINK_REMOVED,
            subject_id=link_request.technical_asset_id,
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
