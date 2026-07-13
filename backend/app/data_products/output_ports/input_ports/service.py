import copy
from datetime import datetime, timedelta, timezone
from typing import Optional, Sequence
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import asc, or_, select
from sqlalchemy.orm import Session

from app.abstract_data_product.input_ports.model import (
    InputPort as InputPortModel,
)
from app.authorization.role_assignments.enums import DecisionStatus
from app.authorization.role_assignments.output_port.model import (
    DatasetRoleAssignment as DatasetRoleAssignmentModel,
)
from app.core.authz import Action, Authorization
from app.core.logging.posthog_analytics import get_posthog_client
from app.data_products.output_ports.model import Dataset
from app.data_products.output_ports.model import Dataset as DatasetModel
from app.users.schema import User
from app.users.schema_response import (
    InputPortRequest,
)


class InputPortService:
    def __init__(self, db: Session):
        self.db = db
        self.posthog = get_posthog_client()

    def get_link_by_id(self, id: UUID) -> InputPortModel:
        current_link = self.db.get(InputPortModel, id)
        if not current_link:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Data product input port not found",
            )
        return current_link

    def get_link(
        self,
        data_product_id: UUID,
        output_port_id: UUID,
        consuming_data_product_id: UUID,
    ) -> InputPortModel:
        current_link = self.db.scalar(
            select(InputPortModel)
            .where(
                InputPortModel.consuming_abstract_data_product_id
                == consuming_data_product_id,
                InputPortModel.dataset_id == output_port_id,
            )
            .join(
                Dataset,
                Dataset.id == InputPortModel.dataset_id,
            )
            .where(
                Dataset.data_product_id == data_product_id,
            )
        )
        if not current_link:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Data product input port not found",
            )
        return current_link

    def approve_output_port_as_input_port(
        self,
        *,
        data_product_id: UUID,
        output_port_id: UUID,
        consuming_data_product_id: UUID,
        actor: User,
        decision_note: Optional[str] = None,
    ) -> InputPortModel:
        current_link = self.get_link(
            data_product_id, output_port_id, consuming_data_product_id
        )
        if current_link.status != DecisionStatus.PENDING:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Approval request already decided",
            )

        current_link.status = DecisionStatus.APPROVED
        current_link.approved_by = actor
        current_link.approved_on = datetime.now(timezone.utc)
        current_link.decision_note = decision_note

        consuming_data_product = current_link.consuming_abstract_data_product

        if self.posthog:
            self.posthog.capture(
                distinct_id=actor.id,
                event="Input Port Approved",
                properties={
                    "data_product_id": str(data_product_id),
                    "output_port_id": str(output_port_id),
                    "consuming_data_product_id": str(consuming_data_product_id),
                    "type": str(
                        consuming_data_product.abstract_data_product_type.value
                    ),
                },
            )

        return current_link

    def deny_output_port_as_input_port(
        self,
        *,
        data_product_id: UUID,
        output_port_id: UUID,
        consuming_data_product_id: UUID,
        actor: User,
        decision_note: str,
    ) -> InputPortModel:
        current_link = self.get_link(
            data_product_id, output_port_id, consuming_data_product_id
        )
        if current_link.status not in (DecisionStatus.PENDING, DecisionStatus.APPROVED):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Approval request already decided",
            )

        current_link.status = DecisionStatus.DENIED
        current_link.denied_by = actor
        current_link.denied_on = datetime.now(timezone.utc)
        current_link.decision_note = decision_note
        return current_link

    def remove_output_port_as_input_port(
        self,
        *,
        data_product_id: UUID,
        output_port_id: UUID,
        consuming_data_product_id: UUID,
    ) -> InputPortModel:
        current_link = self.get_link(
            data_product_id, output_port_id, consuming_data_product_id
        )
        result = copy.deepcopy(current_link)
        self.db.delete(current_link)
        return result

    def get_user_pending_actions(self, user: User) -> Sequence[InputPortRequest]:
        requested_associations = (
            self.db.scalars(
                select(InputPortModel)
                .where(InputPortModel.status == DecisionStatus.PENDING)
                .where(
                    InputPortModel.dataset.has(
                        DatasetModel.assignments.any(
                            DatasetRoleAssignmentModel.user_id == user.id
                        )
                    )
                )
                .order_by(asc(InputPortModel.requested_on))
            )
            .unique()
            .all()
        )

        authorizer = Authorization()
        return [
            InputPortRequest.model_validate(a)
            for a in requested_associations
            if authorizer.has_access(
                sub=str(user.id),
                dom=str(a.dataset.data_product.domain),
                obj=str(a.dataset_id),
                act=Action.OUTPUT_PORT__APPROVE_DATAPRODUCT_ACCESS_REQUEST,
            )
        ]

    def get_user_requests(
        self, user: User, hide_old_inactive: bool
    ) -> Sequence[InputPortRequest]:
        query = (
            select(InputPortModel)
            .where(InputPortModel.requested_by_id == user.id)
            .order_by(asc(InputPortModel.requested_on))
        )

        if hide_old_inactive:
            thirty_days_ago = datetime.now(timezone.utc) - timedelta(days=30)
            query = query.where(
                or_(
                    InputPortModel.status == DecisionStatus.PENDING,
                    InputPortModel.requested_on >= thirty_days_ago,
                )
            )

        requested_associations = self.db.scalars(query).unique().all()

        return requested_associations
