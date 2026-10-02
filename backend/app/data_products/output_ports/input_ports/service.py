from dataclasses import dataclass
from datetime import date, datetime, timedelta, timezone
from typing import Optional, Sequence
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import asc, or_, select
from sqlalchemy.orm import Session, selectinload

from app.abstract_data_product.input_ports.enums import (
    InputPortRequestDecision,
    InputPortStatus,
    RenewalStatus,
)
from app.abstract_data_product.input_ports.model import (
    InputPort as InputPortModel,
)
from app.abstract_data_product.input_ports.model import (
    InputPortRequest as InputPortRequestModel,
)
from app.abstract_data_product.model import AbstractDataProduct
from app.abstract_data_product.type import AbstractDataProductType
from app.authorization.role_assignments.data_product.model import (
    DataProductRoleAssignment as DataProductRoleAssignmentModel,
)
from app.authorization.role_assignments.output_port.model import (
    DatasetRoleAssignment as DatasetRoleAssignmentModel,
)
from app.configuration.access_durations.enums import AccessDurationType
from app.core.authz import Action, Authorization
from app.core.logging.posthog_analytics import (
    PosthogAnalyticsClient,
)
from app.data_products.model import DataProduct as DataProductModel
from app.data_products.output_ports.input_ports.schema_response import (
    OutputPortInputPort,
)
from app.data_products.output_ports.model import OutputPort
from app.data_products.output_ports.model import OutputPort as OutputPortModel
from app.data_products.output_ports.schema_response import (
    output_port_not_found_exception,
)
from app.database.database import UNFILTERED
from app.events.enums import EventReferenceEntity, EventType
from app.events.model import Event as EventModel
from app.events.schema import CreateEvent
from app.events.service import EventService
from app.groups.service import GroupService
from app.settings import settings
from app.users.model import User as UserModel
from app.users.notifications.service import NotificationService
from app.users.schema import User
from app.users.schema_response import (
    InputPortRequest,
)


@dataclass
class RedactedInputPort:
    output_port_id: UUID
    consuming_abstract_data_product_id: UUID
    consuming_abstract_data_product_type: AbstractDataProductType
    status: InputPortStatus
    requested_by_id: UUID

    @staticmethod
    def of(link: InputPortModel, requested_by_id: UUID) -> "RedactedInputPort":
        return RedactedInputPort(
            output_port_id=link.output_port_id,
            consuming_abstract_data_product_id=link.consuming_abstract_data_product_id,
            consuming_abstract_data_product_type=link.consuming_abstract_data_product.abstract_data_product_type,
            status=link.status,
            requested_by_id=requested_by_id,
        )


class InputPortService:
    def __init__(self, db: Session):
        self.db = db
        self.posthog = PosthogAnalyticsClient()

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
        execution_options: Optional[dict] = None,
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
            .options(selectinload(InputPortModel.requests))
            .execution_options(**(execution_options or {})),
        )
        if not current_link:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Data product input port not found",
            )
        return current_link

    def _sync_hidden_data_product_access(self, data_product_id: UUID) -> None:
        from app.data_products.service import DataProductService

        DataProductService(self.db)._sync_consumer_reader_grouping(data_product_id)

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
        request.input_port.recompute_status()
        self.db.flush()
        self._sync_hidden_data_product_access(
            request.input_port.output_port.data_product_id
        )

    def approve_output_port_as_input_port(
        self,
        *,
        data_product_id: UUID,
        output_port_id: UUID,
        consuming_data_product_id: UUID,
        actor: User,
        decision_note: Optional[str] = None,
    ) -> RedactedInputPort:
        current_link = self.get_link(
            data_product_id,
            output_port_id,
            consuming_data_product_id,
            execution_options={"skip_data_product_visibility_filter": True},
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

        self.posthog.capture(
            distinct_id=actor.id,
            event="Input Port Approved",
            properties={
                "data_product_id": str(data_product_id),
                "output_port_id": str(output_port_id),
                "consuming_data_product_id": str(consuming_data_product_id),
                "type": str(consuming_data_product.abstract_data_product_type.value),
            },
        )
        # We don't return the raw model, as it might contain sensitive information. See `skip_data_product_visibility_filter`
        # used in the get_link call above. Instead, we return a dataclass with only the relevant information.
        return RedactedInputPort.of(current_link, pending_request.requested_by_id)

    def renew_output_port_as_input_port(
        self,
        *,
        data_product_id: UUID,
        output_port_id: UUID,
        consuming_data_product_id: UUID,
        actor: User,
    ) -> RedactedInputPort:
        from app.abstract_data_product.service import AbstractDataProductService

        current_link = self.get_link(
            data_product_id,
            output_port_id,
            consuming_data_product_id,
            execution_options={"skip_data_product_visibility_filter": True},
        )
        adp_service = AbstractDataProductService(self.db)
        adp_service._ensure_not_deleting(current_link.consuming_abstract_data_product)
        adp_service._ensure_not_deleting(current_link.output_port.data_product)
        if current_link.pending_request is not None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="A request is already pending for this input port",
            )
        active_grant = current_link.active_grant
        if active_grant is not None and active_grant.valid_until is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="This input port already has permanent access; there is nothing to renew",
            )

        previous_request = current_link.latest_request
        access_duration = adp_service._resolve_access_duration(
            current_link.consuming_abstract_data_product, current_link.output_port
        )
        now = datetime.now(timezone.utc)
        request = InputPortRequestModel(
            justification=previous_request.justification,
            requested_by_id=actor.id,
            requested_on=now,
            access_duration_type=access_duration.access_duration_type,
            requested_duration_days=access_duration.days,
            input_port=current_link,
            access_mode_id=previous_request.access_mode_id,
        )
        self.db.add(request)
        self.db.flush()
        self.approve_request(request, now=now, decided_by=actor)

        self.posthog.capture(
            distinct_id=actor.id,
            event="Input Port Approved",
            properties={
                "data_product_id": str(data_product_id),
                "output_port_id": str(output_port_id),
                "consuming_data_product_id": str(consuming_data_product_id),
                "type": str(
                    current_link.consuming_abstract_data_product.abstract_data_product_type.value
                ),
            },
        )
        return RedactedInputPort(
            output_port_id=current_link.output_port_id,
            consuming_abstract_data_product_id=current_link.consuming_abstract_data_product_id,
            requested_by_id=previous_request.requested_by_id,
        )

    def deny_output_port_as_input_port(
        self,
        *,
        data_product_id: UUID,
        output_port_id: UUID,
        consuming_data_product_id: UUID,
        actor: User,
        decision_note: str,
    ) -> RedactedInputPort:
        current_link = self.get_link(
            data_product_id,
            output_port_id,
            consuming_data_product_id,
            execution_options={"skip_data_product_visibility_filter": True},
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

        # We don't return the raw model, as it might contain sensitive information. See `skip_data_product_visibility_filter`
        # used in the get_link call above. Instead, we return a dataclass with only the relevant information.
        return RedactedInputPort.of(
            current_link, current_link.latest_request.requested_by_id
        )

    def revoke_output_port_as_input_port(
        self,
        *,
        data_product_id: UUID,
        output_port_id: UUID,
        consuming_data_product_id: UUID,
        actor: User,
    ) -> RedactedInputPort:
        current_link = self.get_link(
            data_product_id,
            output_port_id,
            consuming_data_product_id,
            execution_options={"skip_data_product_visibility_filter": True},
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
        self._sync_hidden_data_product_access(data_product_id)
        return RedactedInputPort.of(
            current_link, current_link.latest_request.requested_by_id
        )

    def remove_output_port_as_input_port(
        self,
        *,
        data_product_id: UUID,
        output_port_id: UUID,
        consuming_data_product_id: UUID,
    ) -> RedactedInputPort:
        current_link = self.get_link(
            data_product_id,
            output_port_id,
            consuming_data_product_id,
            execution_options={"skip_data_product_visibility_filter": True},
        )
        result = RedactedInputPort.of(
            current_link, current_link.latest_request.requested_by_id
        )
        self.db.delete(current_link)
        self.db.flush()
        self._sync_hidden_data_product_access(data_product_id)
        return result

    def notify_if_expiring_soon(
        self, input_port: InputPortModel, system_actor_id: UUID
    ) -> bool:
        grant = input_port.active_grant
        if (
            input_port.status != InputPortStatus.APPROVED
            or grant is None
            or grant.valid_until is None
            or input_port.renewal_status == RenewalStatus.PENDING
            or not 0
            <= (grant.valid_until - date.today()).days
            <= settings.EXPIRING_SOON_THRESHOLD_DAYS
        ):
            return False
        already_notified = self.db.scalar(
            select(
                select(EventModel.id)
                .where(
                    EventModel.name == EventType.INPUT_PORT_EXPIRING_SOON,
                    EventModel.subject_id == input_port.output_port_id,
                    EventModel.target_id
                    == input_port.consuming_abstract_data_product_id,
                    EventModel.created_on >= grant.requested_on,
                )
                .exists()
            )
        )
        if already_notified:
            return False
        event_id = EventService(self.db).create_event(
            CreateEvent(
                name=EventType.INPUT_PORT_EXPIRING_SOON,
                subject_id=input_port.output_port_id,
                subject_type=EventReferenceEntity.DATASET,
                target_id=input_port.consuming_abstract_data_product_id,
                target_type=EventReferenceEntity.for_consumer(
                    input_port.consuming_abstract_data_product.abstract_data_product_type
                ),
                actor_id=system_actor_id,
            )
        )
        NotificationService(self.db).create_consumer_notifications(
            consumer_id=input_port.consuming_abstract_data_product_id,
            event_id=event_id,
            extra_receiver_ids=[grant.requested_by_id],
        )
        return True

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
            ),
            execution_options={"skip_data_product_visibility_filter": True},
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
        user_group_ids = GroupService(self.db).get_groups_ids_identity_is_member_of(
            user.id
        )
        requested_associations = (
            self.db.scalars(
                select(InputPortRequestModel)
                .join(InputPortModel)
                .where(
                    InputPortRequestModel.decision == InputPortRequestDecision.PENDING
                )
                .where(
                    or_(
                        InputPortModel.output_port.has(
                            OutputPortModel.assignments.any(
                                DatasetRoleAssignmentModel.user_id == user.id
                            )
                        ),
                        InputPortModel.output_port.has(
                            OutputPortModel.data_product.has(
                                or_(
                                    DataProductRoleAssignmentModel.identity_id
                                    == user.id,
                                    DataProductRoleAssignmentModel.identity_id.in_(
                                        user_group_ids
                                    ),
                                )
                            )
                        ),
                    )
                )
                .options(
                    selectinload(InputPortRequestModel.input_port).selectinload(
                        InputPortModel.requests
                    )
                )
                .order_by(asc(InputPortRequestModel.created_on)),
                # Skip since we will authorize and redact manually
                execution_options=UNFILTERED,
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
                parent=str(a.input_port.output_port.data_product_id),
                act=Action.OUTPUT_PORT__APPROVE_DATAPRODUCT_ACCESS_REQUEST,
            )
        ]

    def get_user_requests(
        self, user: User, hide_old_inactive: bool
    ) -> Sequence[InputPortRequest]:
        query = (
            select(InputPortRequestModel)
            .join(InputPortModel)
            .join(InputPortModel.output_port)
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

        # We skip visibility because we will redact manually
        requests = (
            self.db.scalars(
                query, execution_options={"skip_data_product_visibility_filter": True}
            )
            .unique()
            .all()
        )

        return [self.compute_redaction(user, request) for request in requests]
