from datetime import datetime
from typing import Sequence
from uuid import UUID

import pytz
from fastapi import HTTPException, status
from sqlalchemy import asc, select
from sqlalchemy.orm import Session

from app.core.authz import Action, Authorization
from app.core.aws.refresh_infrastructure_lambda import RefreshInfrastructureLambda
from app.data_products_datasets.model import (
    DataProductDatasetAssociation as DataProductDatasetAssociationModel,
)
from app.datasets.model import Dataset as DatasetModel
from app.events.enum import EventReferenceEntity, EventType
from app.events.schema import CreateEvent
from app.events.service import EventService
from app.notifications.service import NotificationService
from app.pending_actions.schema import DataProductDatasetPendingAction
from app.role_assignments.dataset.model import DatasetRoleAssignment
from app.role_assignments.enums import DecisionStatus
from app.users.schema import User


class DataProductDatasetService:
    def approve_data_product_link(
        self, id: UUID, db: Session, authenticated_user: User
    ) -> None:
        current_link = db.get(DataProductDatasetAssociationModel, id)
        if current_link.status != DecisionStatus.PENDING:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Approval request already decided",
            )

        current_link.status = DecisionStatus.APPROVED
        current_link.approved_by = authenticated_user
        current_link.approved_on = datetime.now(tz=pytz.utc)

        event_id = EventService().create_event(
            db,
            CreateEvent(
                name=EventType.DATA_PRODUCT_DATASET_LINK_APPROVED,
                subject_id=current_link.dataset_id,
                subject_type=EventReferenceEntity.DATASET,
                target_id=current_link.data_product_id,
                target_type=EventReferenceEntity.DATA_PRODUCT,
                actor_id=authenticated_user.id,
            ),
        )
        NotificationService().create_dataset_notifications(
            db, current_link.dataset_id, event_id, [current_link.requested_by_id]
        )
        RefreshInfrastructureLambda().trigger()
        db.commit()

    def deny_data_product_link(
        self, id: UUID, db: Session, authenticated_user: User
    ) -> None:
        current_link = db.get(DataProductDatasetAssociationModel, id)
        if (
            current_link.status != DecisionStatus.PENDING
            and current_link.status != DecisionStatus.APPROVED
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Approval request already decided",
            )
        current_link.status = DecisionStatus.DENIED
        current_link.denied_by = authenticated_user
        current_link.denied_on = datetime.now(tz=pytz.utc)
        event_id = EventService().create_event(
            db,
            CreateEvent(
                name=EventType.DATA_PRODUCT_DATASET_LINK_DENIED,
                subject_id=current_link.dataset_id,
                subject_type=EventReferenceEntity.DATASET,
                target_id=current_link.data_product_id,
                target_type=EventReferenceEntity.DATA_PRODUCT,
                actor_id=authenticated_user.id,
            ),
        )
        NotificationService().create_dataset_notifications(
            db, current_link.dataset_id, event_id, [current_link.requested_by_id]
        )
        db.commit()

    def remove_data_product_link(
        self, id: UUID, db: Session, authenticated_user: User
    ) -> None:
        current_link = db.get(DataProductDatasetAssociationModel, id)
        if not current_link:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Dataset data product link {id} not found",
            )
        event_id = EventService().create_event(
            db,
            CreateEvent(
                name=EventType.DATA_PRODUCT_DATASET_LINK_REMOVED,
                subject_id=current_link.dataset_id,
                subject_type=EventReferenceEntity.DATASET,
                target_id=current_link.data_product_id,
                target_type=EventReferenceEntity.DATA_PRODUCT,
                actor_id=authenticated_user.id,
            ),
        )
        if current_link.status == DecisionStatus.APPROVED:
            NotificationService().create_dataset_notifications(
                db, current_link.dataset_id, event_id, [current_link.requested_by_id]
            )
        db.delete(current_link)
        RefreshInfrastructureLambda().trigger()
        db.commit()

    def get_user_pending_actions(
        self, db: Session, user: User
    ) -> Sequence[DataProductDatasetPendingAction]:
        requested_associations = (
            db.scalars(
                select(DataProductDatasetAssociationModel)
                .where(
                    DataProductDatasetAssociationModel.status == DecisionStatus.PENDING
                )
                .where(
                    DataProductDatasetAssociationModel.dataset.has(
                        DatasetModel.assignments.any(
                            DatasetRoleAssignment.user_id == user.id
                        )
                    )
                )
                .order_by(asc(DataProductDatasetAssociationModel.requested_on))
            )
            .unique()
            .all()
        )

        authorizer = Authorization()
        return [
            a
            for a in requested_associations
            if authorizer.has_access(
                sub=str(user.id),
                dom=str(a.dataset.domain),
                obj=str(a.dataset_id),
                act=Action.DATASET__APPROVE_DATAPRODUCT_ACCESS_REQUEST,
            )
        ]
