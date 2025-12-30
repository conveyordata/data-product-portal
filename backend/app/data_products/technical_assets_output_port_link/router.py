from typing import Sequence
from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.auth.auth import get_authenticated_user
from app.core.authz import Action, Authorization, DataOutputDatasetAssociationResolver
from app.core.authz.resolvers import TechnicalAssetOutputPortLinkResolver
from app.core.aws.refresh_infrastructure_lambda import RefreshInfrastructureLambda
from app.data_products.technical_assets.router import (
    unlink_output_port_from_technical_asset,
)
from app.data_products.technical_assets_output_port_link.schema_request import (
    ApproveLinkBetweenTechnicalAssetAndOutputPortRequest,
    DenyLinkBetweenTechnicalAssetAndOutputPortRequest,
)
from app.data_products.technical_assets_output_port_link.service import (
    DataOutputDatasetService,
)
from app.database.database import get_db_session
from app.events.enums import EventReferenceEntity, EventType
from app.events.schema import CreateEvent
from app.events.service import EventService
from app.notifications.service import NotificationService
from app.pending_actions.schema import DataOutputDatasetPendingAction
from app.users.schema import User

router = APIRouter(tags=["Data Products - Technical assets"])

old_route = "/data_output_dataset_links"
route = "/v2/data_products/{data_product_id}/technical_assets"


@router.post(
    f"{old_route}/approve/{{id}}",
    dependencies=[
        Depends(
            Authorization.enforce(
                Action.DATASET__APPROVE_DATA_OUTPUT_LINK_REQUEST,
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
    approve_link_between_technical_asset_and_output_port(
        data_product_id=link.dataset.data_product_id,
        technical_asset_id=link.data_output_id,
        request=ApproveLinkBetweenTechnicalAssetAndOutputPortRequest(
            output_port_id=link.dataset_id
        ),
        db=db,
        authenticated_user=authenticated_user,
    )


@router.post(
    f"{route}/{{technical_asset_id}}/approve_output_port_link",
    dependencies=[
        Depends(
            Authorization.enforce(
                Action.DATASET__APPROVE_DATA_OUTPUT_LINK_REQUEST,
                TechnicalAssetOutputPortLinkResolver,
                object_id="output_port_id",
            )
        )
    ],
)
def approve_link_between_technical_asset_and_output_port(
    data_product_id: UUID,
    technical_asset_id: UUID,
    request: ApproveLinkBetweenTechnicalAssetAndOutputPortRequest,
    db: Session = Depends(get_db_session),
    authenticated_user: User = Depends(get_authenticated_user),
):
    output_link = DataOutputDatasetService(db).approve_data_output_link(
        data_product_id=data_product_id,
        technical_asset_id=technical_asset_id,
        output_port_id=request.output_port_id,
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
                Action.DATASET__APPROVE_DATA_OUTPUT_LINK_REQUEST,
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
    deny_link_between_technical_asset_and_output_port(
        data_product_id=link.dataset.data_product_id,
        technical_asset_id=link.data_output_id,
        request=DenyLinkBetweenTechnicalAssetAndOutputPortRequest(
            output_port_id=link.dataset_id
        ),
        db=db,
        authenticated_user=authenticated_user,
    )


@router.post(
    f"{route}/{{technical_asset_id}}/deny_output_port_link",
    dependencies=[
        Depends(
            Authorization.enforce(
                Action.DATASET__APPROVE_DATA_OUTPUT_LINK_REQUEST,
                TechnicalAssetOutputPortLinkResolver,
                object_id="output_port_id",
            )
        )
    ],
)
def deny_link_between_technical_asset_and_output_port(
    data_product_id: UUID,
    technical_asset_id: UUID,
    request: DenyLinkBetweenTechnicalAssetAndOutputPortRequest,
    db: Session = Depends(get_db_session),
    authenticated_user: User = Depends(get_authenticated_user),
) -> None:
    output_link = DataOutputDatasetService(db).deny_data_output_link(
        data_product_id=data_product_id,
        technical_asset_id=technical_asset_id,
        output_port_id=request.output_port_id,
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
                Action.DATASET__REVOKE_DATA_OUTPUT_LINK,
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
        output_link.data_output_id,
        output_link.dataset_id,
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
