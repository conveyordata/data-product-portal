from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.auth.auth import get_authenticated_user
from app.core.authz import (
    Action,
    Authorization,
    DataProductResolver,
    TechnicalAssetResolver,
)
from app.data_products.technical_assets.model import ensure_technical_asset_exists
from app.data_products.technical_assets.schema_request import (
    CreateTechnicalAssetRequest,
    DataOutputStatusUpdate,
    DataOutputUpdate,
)
from app.data_products.technical_assets.schema_response import (
    CreateTechnicalAssetResponse,
    GetTechnicalAssetsResponse,
    GetTechnicalAssetsResponseItem,
    UpdateTechnicalAssetResponse,
)
from app.data_products.technical_assets.service import TechnicalAssetService
from app.database.database import get_db_session
from app.events.enums import EventReferenceEntity, EventType
from app.events.schema import CreateEvent
from app.events.schema_response import (
    GetEventHistoryResponse,
    GetEventHistoryResponseItemOld,
)
from app.events.service import EventService
from app.graph.graph import Graph
from app.users.notifications.service import NotificationService
from app.users.schema import User

router = APIRouter(
    tags=["Data Products - Technical assets"],
    prefix="/v2/data_products/{data_product_id}/technical_assets",
)


@router.get(
    "/",
    dependencies=[
        Depends(
            Authorization.enforce(
                Action.HIDDEN_DATA_PRODUCT__READ,
                DataProductResolver,
                object_id="data_product_id",
            )
        )
    ],
)
def get_data_product_technical_assets(
    data_product_id: UUID, db: Session = Depends(get_db_session)
) -> GetTechnicalAssetsResponse:
    return GetTechnicalAssetsResponse(
        technical_assets=[
            GetTechnicalAssetsResponseItem.model_validate(do)
            for do in TechnicalAssetService(db).get_technical_assets_for_data_product(
                data_product_id
            )
        ]
    )


@router.get(
    "/{id}",
    dependencies=[
        Depends(
            Authorization.enforce(
                Action.HIDDEN_DATA_PRODUCT__READ,
                DataProductResolver,
                object_id="data_product_id",
            )
        )
    ],
)
def get_technical_asset(
    data_product_id: UUID, id: UUID, db: Session = Depends(get_db_session)
) -> GetTechnicalAssetsResponseItem:
    return GetTechnicalAssetsResponseItem.model_validate(
        TechnicalAssetService(db).get_technical_asset(data_product_id, id)
    )


@router.get(
    "/{id}/history",
    dependencies=[
        Depends(
            Authorization.enforce(
                Action.HIDDEN_DATA_PRODUCT__READ,
                DataProductResolver,
                object_id="data_product_id",
            )
        )
    ],
)
def get_technical_asset_event_history(
    data_product_id: UUID, id: UUID, db: Session = Depends(get_db_session)
) -> GetEventHistoryResponse:
    ensure_technical_asset_exists(id, db, data_product_id=data_product_id)
    return GetEventHistoryResponse(
        events=[
            GetEventHistoryResponseItemOld.model_validate(event).convert()
            for event in EventService(db).get_history(
                id, EventReferenceEntity.DATA_OUTPUT
            )
        ]
    )


@router.delete(
    "/{id}",
    responses={
        404: {
            "description": "Technical asset not found",
            "content": {
                "application/json": {
                    "example": {"detail": "Technical asset id not found"}
                }
            },
        }
    },
    dependencies=[
        Depends(
            Authorization.enforce(
                Action.DATA_PRODUCT__DELETE_TECHNICAL_ASSET,
                TechnicalAssetResolver,
            )
        ),
    ],
)
def remove_technical_asset(
    data_product_id: UUID,
    id: UUID,
    db: Session = Depends(get_db_session),
    authenticated_user: User = Depends(get_authenticated_user),
) -> None:
    data_output = TechnicalAssetService(db).remove_data_output(data_product_id, id)
    event_id = EventService(db).create_event(
        CreateEvent(
            name=EventType.DATA_OUTPUT_REMOVED,
            actor_id=authenticated_user.id,
            subject_id=id,
            subject_type=EventReferenceEntity.DATA_OUTPUT,
            deleted_subject_identifier=data_output.name,
            target_id=data_output.owner_id,
            target_type=EventReferenceEntity.DATA_PRODUCT,
            deleted_target_identifier=data_output.owner.name,
        ),
    )
    NotificationService(db).create_data_product_notifications(
        data_product_id=data_output.owner_id, event_id=event_id
    )


@router.put(
    "/{id}",
    responses={
        404: {
            "description": "Technical asset not found",
            "content": {
                "application/json": {
                    "example": {"detail": "Technical asset id not found"}
                }
            },
        }
    },
    dependencies=[
        Depends(
            Authorization.enforce(
                Action.DATA_PRODUCT__UPDATE_TECHNICAL_ASSET,
                TechnicalAssetResolver,
            )
        ),
    ],
)
def update_technical_asset(
    data_product_id: UUID,
    id: UUID,
    data_output: DataOutputUpdate,
    db: Session = Depends(get_db_session),
    authenticated_user: User = Depends(get_authenticated_user),
) -> UpdateTechnicalAssetResponse:
    result = TechnicalAssetService(db).update_data_output(
        data_product_id, id, data_output
    )
    EventService(db).create_event(
        CreateEvent(
            name=EventType.DATA_OUTPUT_UPDATED,
            subject_id=id,
            subject_type=EventReferenceEntity.DATA_OUTPUT,
            actor_id=authenticated_user.id,
        )
    )
    return result


@router.put(
    "/{id}/status",
    responses={
        404: {
            "description": "Data Output not found",
            "content": {
                "application/json": {"example": {"detail": "Data Output id not found"}}
            },
        }
    },
    dependencies=[
        Depends(
            Authorization.enforce(
                Action.DATA_PRODUCT__UPDATE_TECHNICAL_ASSET,
                TechnicalAssetResolver,
            )
        ),
    ],
)
def update_technical_asset_status(
    data_product_id: UUID,
    id: UUID,
    data_output: DataOutputStatusUpdate,
    db: Session = Depends(get_db_session),
    authenticated_user: User = Depends(get_authenticated_user),
) -> None:
    TechnicalAssetService(db).update_data_output_status(
        data_product_id, id, data_output, actor=authenticated_user
    )
    EventService(db).create_event(
        CreateEvent(
            name=EventType.DATA_OUTPUT_UPDATED,
            subject_id=id,
            subject_type=EventReferenceEntity.DATA_OUTPUT,
            actor_id=authenticated_user.id,
        )
    )


@router.get(
    "/{id}/graph",
    dependencies=[
        Depends(
            Authorization.enforce(
                Action.HIDDEN_DATA_PRODUCT__READ,
                DataProductResolver,
                object_id="data_product_id",
            )
        )
    ],
)
def get_technical_asset_graph_data(
    data_product_id: UUID,
    id: UUID,
    db: Session = Depends(get_db_session),
    level: int = 3,
) -> Graph:
    return TechnicalAssetService(db).get_graph_data(data_product_id, id, level)


@router.post(
    "/",
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
                Action.DATA_PRODUCT__CREATE_TECHNICAL_ASSET,
                DataProductResolver,
                object_id="data_product_id",
            )
        ),
    ],
)
def create_technical_asset(
    data_product_id: UUID,
    technical_asset: CreateTechnicalAssetRequest,
    db: Session = Depends(get_db_session),
    authenticated_user: User = Depends(get_authenticated_user),
) -> CreateTechnicalAssetResponse:
    technical_asset = TechnicalAssetService(db).create_technical_asset(
        data_product_id, technical_asset
    )
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
    return CreateTechnicalAssetResponse(id=technical_asset.id)
