from typing import Sequence
from uuid import UUID

from fastapi import APIRouter, BackgroundTasks, Depends
from sqlalchemy.orm import Session

from app.core.auth.auth import get_authenticated_user
from app.core.authz import Action, Authorization, DataOutputResolver
from app.core.aws.refresh_infrastructure_lambda import RefreshInfrastructureLambda
from app.core.namespace.validation import NamespaceLengthLimits, NamespaceSuggestion
from app.data_products.output_port_technical_assets_link.router import (
    link_output_port_to_technical_asset,
    unlink_output_port_from_technical_asset,
)
from app.data_products.output_port_technical_assets_link.schema_request import (
    LinkTechnicalAssetToOutputPortRequest,
    UnLinkTechnicalAssetToOutputPortRequest,
)
from app.data_products.output_port_technical_assets_link.schema_response import (
    LinkTechnicalAssetsToOutputPortResponse,
)
from app.data_products.technical_assets.model import ensure_data_output_exists
from app.data_products.technical_assets.schema_request import (
    DataOutputResultStringRequest,
    DataOutputStatusUpdate,
    DataOutputUpdate,
)
from app.data_products.technical_assets.schema_response import (
    DataOutputGet,
    DataOutputsGet,
    GetTechnicalAssetsResponseItem,
    UpdateTechnicalAssetResponse,
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
from app.resource_names.service import ResourceNameService
from app.users.notifications.service import NotificationService
from app.users.schema import User

old_route = "/data_outputs"
route = "/v2/data_products/{data_product_id}/technical_assets"
router = APIRouter(tags=["Data Products - Technical assets"])


@router.get(old_route, deprecated=True)
def get_data_outputs(db: Session = Depends(get_db_session)) -> Sequence[DataOutputsGet]:
    return DataOutputService(db).get_data_outputs()


@router.get(f"{old_route}/namespace_suggestion", deprecated=True)
def get_dataset_namespace_suggestion(name: str) -> NamespaceSuggestion:
    return NamespaceSuggestion(
        namespace=ResourceNameService.resource_name_suggestion(name).resource_name
    )


@router.get(f"{old_route}/namespace_length_limits", deprecated=True)
def get_dataset_namespace_length_limits() -> NamespaceLengthLimits:
    return NamespaceLengthLimits(
        max_length=ResourceNameService.resource_name_length_limits().max_length
    )


@router.post(f"{old_route}/result_string", deprecated=True)
def get_data_output_result_string(
    request: DataOutputResultStringRequest, db: Session = Depends(get_db_session)
) -> str:
    return DataOutputService(db).get_data_output_result_string(request)


@router.get(f"{old_route}/{{id}}", deprecated=True)
def get_data_output(id: UUID, db: Session = Depends(get_db_session)) -> DataOutputGet:
    do = ensure_data_output_exists(id, db)
    return DataOutputService(db).get_data_output(do.owner_id, id)


@router.get(f"{route}/{{id}}")
def get_technical_asset(
    data_product_id: UUID, id: UUID, db: Session = Depends(get_db_session)
) -> GetTechnicalAssetsResponseItem:
    return DataOutputGet.model_validate(
        DataOutputService(db).get_data_output(data_product_id, id)
    ).convert()


@router.get(f"{old_route}/{{id}}/history", deprecated=True)
def get_data_output_event_history(
    id: UUID, db: Session = Depends(get_db_session)
) -> Sequence[GetEventHistoryResponseItemOld]:
    return EventService(db).get_history(id, EventReferenceEntity.DATA_OUTPUT)


@router.get(f"{route}/{{id}}/history")
def get_technical_asset_event_history(
    data_product_id: UUID, id: UUID, db: Session = Depends(get_db_session)
) -> GetEventHistoryResponse:
    ensure_data_output_exists(id, db, data_product_id=data_product_id)
    return GetEventHistoryResponse(
        events=[
            GetEventHistoryResponseItemOld.model_validate(event).convert()
            for event in EventService(db).get_history(
                id, EventReferenceEntity.DATA_OUTPUT
            )
        ]
    )


@router.delete(
    f"{old_route}/{{id}}",
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
                Action.DATA_PRODUCT__DELETE_DATA_OUTPUT,
                DataOutputResolver,
            )
        ),
    ],
    deprecated=True,
)
def remove_data_output(
    id: UUID,
    db: Session = Depends(get_db_session),
    authenticated_user: User = Depends(get_authenticated_user),
) -> None:
    data_output = ensure_data_output_exists(id, db)
    return remove_technical_asset(data_output.owner_id, id, db, authenticated_user)


@router.delete(
    f"{route}/{{id}}",
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
                Action.DATA_PRODUCT__DELETE_DATA_OUTPUT,
                DataOutputResolver,
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
    data_output = DataOutputService(db).remove_data_output(data_product_id, id)
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
    RefreshInfrastructureLambda().trigger()


@router.put(
    f"{old_route}/{{id}}",
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
                Action.DATA_PRODUCT__UPDATE_DATA_OUTPUT,
                DataOutputResolver,
            )
        ),
    ],
    deprecated=True,
)
def update_data_output(
    id: UUID,
    data_output: DataOutputUpdate,
    db: Session = Depends(get_db_session),
    authenticated_user: User = Depends(get_authenticated_user),
) -> UpdateTechnicalAssetResponse:
    do = ensure_data_output_exists(id, db)
    return update_technical_asset(do.owner_id, id, data_output, db, authenticated_user)


@router.put(
    f"{route}/{{id}}",
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
                Action.DATA_PRODUCT__UPDATE_DATA_OUTPUT,
                DataOutputResolver,
            )
        ),
    ],
    deprecated=True,
)
def update_technical_asset(
    data_product_id: UUID,
    id: UUID,
    data_output: DataOutputUpdate,
    db: Session = Depends(get_db_session),
    authenticated_user: User = Depends(get_authenticated_user),
) -> UpdateTechnicalAssetResponse:
    result = DataOutputService(db).update_data_output(data_product_id, id, data_output)
    EventService(db).create_event(
        CreateEvent(
            name=EventType.DATA_OUTPUT_UPDATED,
            subject_id=id,
            subject_type=EventReferenceEntity.DATA_OUTPUT,
            actor_id=authenticated_user.id,
        )
    )
    RefreshInfrastructureLambda().trigger()
    return result


@router.put(
    f"{old_route}/{{id}}/status",
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
                Action.DATA_PRODUCT__UPDATE_DATA_OUTPUT,
                DataOutputResolver,
            )
        ),
    ],
    deprecated=True,
)
def update_data_output_status(
    id: UUID,
    data_output: DataOutputStatusUpdate,
    db: Session = Depends(get_db_session),
    authenticated_user: User = Depends(get_authenticated_user),
) -> None:
    do = ensure_data_output_exists(id, db)
    return update_technical_asset_status(
        do.owner_id, id, data_output, db, authenticated_user
    )


@router.put(
    f"{route}/{{id}}/status",
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
                Action.DATA_PRODUCT__UPDATE_DATA_OUTPUT,
                DataOutputResolver,
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
    DataOutputService(db).update_data_output_status(
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


@router.post(
    f"{old_route}/{{id}}/dataset/{{dataset_id}}",
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
                Action.DATA_PRODUCT__REQUEST_DATA_OUTPUT_LINK,
                DataOutputResolver,
            )
        ),
    ],
    deprecated=True,
)
def link_dataset_to_data_output(
    id: UUID,
    dataset_id: UUID,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db_session),
    authenticated_user: User = Depends(get_authenticated_user),
) -> LinkTechnicalAssetsToOutputPortResponse:
    do = ensure_data_output_exists(id, db)
    return link_output_port_to_technical_asset(
        do.owner_id,
        dataset_id,
        LinkTechnicalAssetToOutputPortRequest(technical_asset_id=do.id),
        background_tasks,
        db,
        authenticated_user,
    )


@router.delete(
    f"{old_route}/{{id}}/dataset/{{dataset_id}}",
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
                Action.DATA_PRODUCT__REVOKE_DATASET_ACCESS,
                DataOutputResolver,
            )
        ),
    ],
    deprecated=True,
)
def unlink_dataset_from_data_output(
    id: UUID,
    dataset_id: UUID,
    db: Session = Depends(get_db_session),
    authenticated_user: User = Depends(get_authenticated_user),
) -> None:
    do = ensure_data_output_exists(id, db)
    return unlink_output_port_from_technical_asset(
        data_product_id=do.owner_id,
        output_port_id=dataset_id,
        request=UnLinkTechnicalAssetToOutputPortRequest(technical_asset_id=id),
        db=db,
        authenticated_user=authenticated_user,
    )


@router.get(f"{old_route}/{{id}}/graph", deprecated=True)
def get_graph_data_old(
    id: UUID, db: Session = Depends(get_db_session), level: int = 3
) -> Graph:
    do = ensure_data_output_exists(id, db)
    return get_technical_asset_graph_data(
        data_product_id=do.owner_id, id=id, db=db, level=level
    )


@router.get(f"{route}/{{id}}/graph")
def get_technical_asset_graph_data(
    data_product_id: UUID,
    id: UUID,
    db: Session = Depends(get_db_session),
    level: int = 3,
) -> Graph:
    return DataOutputService(db).get_graph_data(data_product_id, id, level)
