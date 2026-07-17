import copy
from datetime import datetime, timedelta, timezone
from typing import Optional, Sequence
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import asc, or_, select
from sqlalchemy.orm import Session, selectinload

from app.abstract_data_product.input_ports.enums import InputPortStatus
from app.abstract_data_product.input_ports.model import (
    InputPort as InputPortModel,
)
from app.abstract_data_product.input_ports.model import (
    InputPortRequest as InputPortRequestModel,
)
from app.access_durations.enums import AccessDurationType
from app.authorization.role_assignments.enums import DecisionStatus
from app.authorization.role_assignments.output_port.model import (
    DatasetRoleAssignment as DatasetRoleAssignmentModel,
)
from app.core.authz import Action, Authorization
from app.core.logging.posthog_analytics import get_posthog_client
from app.data_products.output_ports.model import OutputPort
from app.data_products.output_ports.model import OutputPort as OutputPortModel
from app.users.model import User as UserModel
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
                InputPortModel.output_port_id == output_port_id,
            )
            .join(
                OutputPort,
                OutputPort.id == InputPortModel.output_port_id,
            )
            .where(
                OutputPort.data_product_id == data_product_id,
            )
            .options(selectinload(InputPortModel.requests)),
        )
        if not current_link:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Data product input port not found",
            )
        return current_link

    def approve_request(
        self,
        request: InputPortRequestModel,
        *,
        now: datetime,
        decided_by: Optional[UserModel] = None,
        decision_note: Optional[str] = None,
    ) -> None:
        request.valid_from = now
        request.decided_on = now
        request.decided_by = decided_by
        request.decision_note = decision_note
        request.decision = DecisionStatus.APPROVED
        request.input_port.status = InputPortStatus.APPROVED

        match request.access_duration_type:
            case AccessDurationType.PERMANENT:
                request.valid_until = None
            case AccessDurationType.TIME_BOUND:
                if request.requested_duration_days is None:
                    raise HTTPException(
                        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        detail="Requested duration days is required for TIME_BOUND access duration type",
                    )
                request.valid_until = now.date() + timedelta(
                    days=request.requested_duration_days
                )

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

        pending_request = current_link.latest_request
        if (
            pending_request is None
            or pending_request.decision != DecisionStatus.PENDING
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="There is no pending request",
            )
        self.approve_request(
            pending_request,
            now=datetime.now(timezone.utc),
            decided_by=actor,
            decision_note=decision_note,
        )

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

        pending_request: Optional[InputPortRequestModel] = self.db.scalar(
            select(InputPortRequestModel).where(
                InputPortRequestModel.decision.in_(
                    [DecisionStatus.PENDING, DecisionStatus.APPROVED]
                ),
                InputPortRequestModel.input_port_id == current_link.id,
            )
        )
        if pending_request is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="There is no pending or approved request to deny",
            )

        current_link.status = InputPortStatus.DENIED
        pending_request.decided_by = actor
        pending_request.decided_on = datetime.now(timezone.utc)
        pending_request.decision_note = decision_note
        pending_request.decision = DecisionStatus.DENIED
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

    # Future refactor: query and return InputPortRequests instead of InputPorts
    def get_user_pending_actions(self, user: User) -> Sequence[InputPortRequest]:
        requested_associations = (
            self.db.scalars(
                select(InputPortModel)
                .join(InputPortRequestModel)
                .where(InputPortRequestModel.decision == DecisionStatus.PENDING)
                .where(
                    InputPortModel.output_port.has(
                        OutputPortModel.assignments.any(
                            DatasetRoleAssignmentModel.user_id == user.id
                        )
                    )
                )
                .options(selectinload(InputPortModel.requests))
                .order_by(asc(InputPortRequestModel.requested_on))
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
                dom=str(a.output_port.data_product.domain),
                obj=str(a.output_port_id),
                act=Action.OUTPUT_PORT__APPROVE_DATAPRODUCT_ACCESS_REQUEST,
            )
        ]

    # Future refactor: query and return InputPortRequests instead of InputPorts
    def get_user_requests(
        self, user: User, hide_old_inactive: bool
    ) -> Sequence[InputPortRequest]:
        query = (
            select(InputPortModel)
            .join(InputPortRequestModel)
            .where(InputPortRequestModel.requested_by_id == user.id)
            .options(selectinload(InputPortModel.requests))
            .order_by(asc(InputPortRequestModel.requested_on))
        )

        if hide_old_inactive:
            thirty_days_ago = datetime.now(timezone.utc) - timedelta(days=30)
            query = query.where(
                or_(
                    InputPortModel.status == InputPortStatus.PENDING,
                    InputPortRequestModel.requested_on >= thirty_days_ago,
                )
            )

        requested_associations = self.db.scalars(query).unique().all()

        return requested_associations
