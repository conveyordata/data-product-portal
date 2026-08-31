import copy
from datetime import datetime, timedelta, timezone
from typing import Optional, Sequence
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import asc, or_, select
from sqlalchemy.orm import Session, selectinload

from app.abstract_data_product.input_ports.enums import (
    InputPortRequestDecision,
)
from app.abstract_data_product.input_ports.model import (
    InputPort as InputPortModel,
)
from app.abstract_data_product.input_ports.model import (
    InputPortRequest as InputPortRequestModel,
)
from app.abstract_data_product.model import AbstractDataProduct
from app.authorization.role_assignments.output_port.model import (
    DatasetRoleAssignment as DatasetRoleAssignmentModel,
)
from app.configuration.access_durations.enums import AccessDurationType
from app.core.authz import Action, Authorization
from app.core.logging.posthog_analytics import get_posthog_client
from app.data_products.model import DataProduct as DataProductModel
from app.data_products.output_ports.input_ports.schema_response import (
    OutputPortInputPort,
)
from app.data_products.output_ports.model import OutputPort
from app.data_products.output_ports.model import OutputPort as OutputPortModel
from app.data_products.output_ports.schema_response import (
    output_port_not_found_exception,
)
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
        request.valid_from = now.date()
        request.decided_on = now
        request.decided_by = decided_by
        request.decision_note = decision_note
        request.decision = InputPortRequestDecision.APPROVED

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
        pending_request = current_link.pending_request
        if pending_request is None:
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
        current_link.recompute_status()

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
        target = current_link.pending_request
        if target is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="There is no pending request to deny",
            )

        target.decided_by = actor
        target.decided_on = datetime.now(timezone.utc)
        target.decision_note = decision_note
        target.decision = InputPortRequestDecision.DENIED
        current_link.recompute_status()
        return current_link

    def revoke_output_port_as_input_port(
        self,
        *,
        data_product_id: UUID,
        output_port_id: UUID,
        consuming_data_product_id: UUID,
        actor: User,
    ) -> InputPortModel:
        current_link = self.get_link(
            data_product_id, output_port_id, consuming_data_product_id
        )
        target = current_link.active_grant
        if target is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="There is no active access to revoke",
            )

        target.revoked_by = actor
        target.revoked_at = datetime.now(timezone.utc)
        current_link.recompute_status()
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

    @staticmethod
    def calculate_redaction_of_consumer(
        current_user: User, consuming_data_product: AbstractDataProduct
    ) -> bool:
        if not isinstance(consuming_data_product, DataProductModel):
            return False
        return not Authorization().has_read_access_to_data_product(
            current_user, consuming_data_product
        )

    def get_consuming_data_products(
        self, current_user: User, output_port_id: UUID, data_product_id: UUID
    ) -> Sequence[OutputPortInputPort]:

        output_port = self.db.scalar(
            select(OutputPortModel)
            .where(OutputPortModel.id == output_port_id)
            .where(OutputPortModel.data_product_id == data_product_id)
            .options(
                selectinload(OutputPortModel.data_product_links).selectinload(
                    InputPortModel.consuming_abstract_data_product
                ),
                selectinload(OutputPortModel.data_product_links).selectinload(
                    InputPortModel.requests
                ),
            )
        )
        if not output_port:
            raise output_port_not_found_exception(output_port_id)

        result = []
        for link in output_port.data_product_links:
            item = OutputPortInputPort.model_validate(link)
            item.consuming_abstract_data_product.set_redacted(
                self.calculate_redaction_of_consumer(
                    current_user, link.consuming_abstract_data_product
                )
            )
            result.append(item)
        return result

    def compute_redaction(
        self, user: User, request: InputPortRequestModel
    ) -> InputPortRequest:
        result = InputPortRequest.model_validate(request)
        result.input_port.consuming_abstract_data_product.set_redacted(
            self.calculate_redaction_of_consumer(
                user, request.input_port.consuming_abstract_data_product
            )
        )
        return result

    def get_user_pending_actions(self, user: User) -> Sequence[InputPortRequest]:
        requested_associations = (
            self.db.scalars(
                select(InputPortRequestModel)
                .join(InputPortModel)
                .where(
                    InputPortRequestModel.decision == InputPortRequestDecision.PENDING
                )
                .where(
                    InputPortModel.output_port.has(
                        OutputPortModel.assignments.any(
                            DatasetRoleAssignmentModel.user_id == user.id
                        )
                    )
                )
                .options(
                    selectinload(InputPortRequestModel.input_port).selectinload(
                        InputPortModel.requests
                    )
                )
                .order_by(asc(InputPortRequestModel.created_on))
            )
            .unique()
            .all()
        )

        authorizer = Authorization()
        return [
            self.compute_redaction(user, a)
            for a in requested_associations
            if authorizer.has_access(
                sub=str(user.id),
                dom=str(a.input_port.output_port.data_product.domain.id),
                obj=str(a.input_port.output_port_id),
                act=Action.OUTPUT_PORT__APPROVE_DATAPRODUCT_ACCESS_REQUEST,
            )
        ]

    def get_user_requests(
        self, user: User, hide_old_inactive: bool
    ) -> Sequence[InputPortRequest]:
        query = (
            select(InputPortRequestModel)
            .join(InputPortModel)
            .where(InputPortRequestModel.requested_by_id == user.id)
            .options(
                selectinload(InputPortRequestModel.input_port).selectinload(
                    InputPortModel.requests
                )
            )
            .order_by(asc(InputPortRequestModel.requested_on))
        )

        if hide_old_inactive:
            thirty_days_ago = datetime.now(timezone.utc) - timedelta(days=30)
            query = query.where(
                or_(
                    InputPortRequestModel.decision == InputPortRequestDecision.PENDING,
                    InputPortRequestModel.requested_on >= thirty_days_ago,
                )
            )

        requests = self.db.scalars(query).unique().all()

        return [self.compute_redaction(user, request) for request in requests]
