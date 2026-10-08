from copy import deepcopy
from datetime import datetime, timezone
from typing import Optional, Sequence
from uuid import UUID

import pytz
from fastapi import BackgroundTasks, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session, contains_eager, selectinload

from app.abstract_data_product.input_ports.enums import InputPortRequestDecision
from app.abstract_data_product.input_ports.model import (
    InputPort as InputPortModel,
)
from app.abstract_data_product.input_ports.model import (
    InputPortRequest as InputPortRequestModel,
)
from app.abstract_data_product.model import (
    AbstractDataProduct,
    ensure_abstract_data_product_exists,
)
from app.abstract_data_product.schema_request import (
    RequestInputPortsForAbstractDataProductRequestItem,
)
from app.abstract_data_product.type import AbstractDataProductType
from app.authorization.role_assignments.output_port.service import (
    RoleAssignmentService as OutputPortRoleAssignmentService,
)
from app.configuration.access_durations.enums import AccessDurationType
from app.configuration.access_durations.model import AccessDuration
from app.configuration.access_durations.service import AccessDurationService
from app.core.authz import Action
from app.core.logging.posthog_analytics import (
    PosthogAnalyticsClient,
)
from app.data_products import email
from app.data_products.output_ports.enums import OutputPortAccessFunction
from app.data_products.output_ports.input_ports.service import (
    InputPortService,
    RedactedInputPort,
)
from app.data_products.output_ports.model import OutputPort as OutputPortModel
from app.data_products.output_ports.model import ensure_output_port_exists
from app.data_products.status import AbstractDataProductStatus
from app.users.model import User


class AbstractDataProductService:
    def __init__(self, db: Session):
        self.db = db
        self.posthog = PosthogAnalyticsClient()

    def _ensure_not_deleting(self, adp: AbstractDataProduct) -> None:
        if adp.status == AbstractDataProductStatus.DELETING:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"{adp.abstract_data_product_type.value} '{adp.name}' is pending deletion and cannot be modified",
            )

    def get_input_ports(self, data_product_id: UUID) -> Sequence[InputPortModel]:
        ensure_abstract_data_product_exists(data_product_id, self.db)
        return (
            self.db.scalars(
                select(InputPortModel)
                # Join (rather than selectinload) the output port so that the
                # private output port visibility filter excludes the whole
                # input port row when its output port isn't visible to the
                # current user, instead of just nulling out the relationship.
                .join(InputPortModel.output_port)
                .options(
                    contains_eager(InputPortModel.output_port),
                    selectinload(InputPortModel.requests),
                )
                .filter(
                    InputPortModel.consuming_abstract_data_product_id == data_product_id
                ),
            )
            .unique()
            .all()
        )

    def _resolve_access_duration(
        self, adp: AbstractDataProduct, output_port: OutputPortModel
    ) -> AccessDuration:
        access_duration_type = self.get_access_duration_type(
            output_port=output_port,
            abstract_data_product_type=adp.abstract_data_product_type,
        )
        access_duration = AccessDurationService(self.db).get_access_duration(
            adp.abstract_data_product_type, access_duration_type
        )
        if access_duration is None:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=(
                    "No access duration is configured for "
                    f"{adp.abstract_data_product_type.value} access to this output port"
                ),
            )
        return access_duration

    def get_access_duration_type(
        self,
        output_port: OutputPortModel,
        abstract_data_product_type: AbstractDataProductType,
    ) -> AccessDurationType:
        match abstract_data_product_type:
            case AbstractDataProductType.DATA_PRODUCT:
                return output_port.data_product_access_duration_type
            case AbstractDataProductType.EXPLORATION:
                return output_port.exploration_access_duration_type
            case _:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=(
                        "Unsupported abstract data product type: "
                        f"{abstract_data_product_type}"
                    ),
                )

    def _create_request(
        self,
        adp: AbstractDataProduct,
        output_port: OutputPortModel,
        input_port: InputPortModel,
        justification: str,
        access_mode_id: Optional[UUID] = None,
        direct_grant: bool = False,
        *,
        actor: User,
    ) -> InputPortModel:
        access_duration = self._resolve_access_duration(adp, output_port)
        request = InputPortRequestModel(
            justification=justification,
            requested_by=actor,
            requested_on=datetime.now(tz=pytz.utc),
            access_duration_type=access_duration.access_duration_type,
            requested_duration_days=access_duration.days,
            input_port=input_port,
            access_mode_id=access_mode_id,
        )
        self.db.add(request)
        self.db.flush()
        if (
            direct_grant
            or output_port.access_function == OutputPortAccessFunction.UNRESTRICTED
        ):
            InputPortService(self.db).approve_request(
                request,
                now=datetime.now(tz=pytz.utc),
                decided_by=actor if direct_grant else None,
                decision_note="Access granted directly by output port owner"
                if direct_grant
                else "Auto approved for unrestricted output port",
            )
        else:
            request.decision = InputPortRequestDecision.PENDING
        input_port.recompute_status()

        if request.decision == InputPortRequestDecision.APPROVED:
            self.posthog.capture(
                distinct_id=actor.id,
                event="Input Port Approved",
                properties={
                    "data_product_id": str(output_port.data_product_id),
                    "output_port_id": str(output_port.id),
                    "consuming_data_product_id": str(adp.id),
                    "type": str(adp.abstract_data_product_type.value),
                },
            )
        return input_port

    def _add_single_input_port(
        self,
        adp: AbstractDataProduct,
        output_port_id: UUID,
        justification: str,
        access_mode_id: Optional[UUID] = None,
        data_product_id: Optional[UUID] = None,
        direct_grant: bool = False,
        *,
        actor: User,
    ) -> InputPortModel:
        output_port = ensure_output_port_exists(
            output_port_id,
            self.db,
            data_product_id=data_product_id,
            options=[
                selectinload(OutputPortModel.data_product_links)
                .selectinload(InputPortModel.consuming_abstract_data_product)
                .selectinload(AbstractDataProduct.input_ports),
            ],
            populate_existing=True,
        )
        self._ensure_not_deleting(adp)
        self._ensure_not_deleting(output_port.data_product)
        existing = next(
            (link for link in adp.input_ports if link.output_port_id == output_port.id),
            None,
        )
        if existing:
            if direct_grant:
                self.db.refresh(existing, ["requests"])
            if not direct_grant or existing.active_grant or existing.pending_request:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Input port connection to Output Port ({output_port_id}) already exists in {adp.abstract_data_product_type} {adp.id}",
                )
        if output_port.data_product_id == adp.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot link own output port to data product",
            )
        if (
            adp.abstract_data_product_type == AbstractDataProductType.EXPLORATION
            and output_port.access_function == OutputPortAccessFunction.PRIVATE
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Explorations cannot consume Invite only output ports",
            )

        if output_port.access_modes and not access_mode_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Can not request access to this output port without specifying an access mode",
            )
        if access_mode_id and access_mode_id not in [
            op.id for op in output_port.access_modes
        ]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="The specified access mode does not exist",
            )

        input_port = existing or InputPortModel(
            output_port=output_port,
            output_port_id=output_port_id,
            consuming_abstract_data_product=adp,
        )
        self._create_request(
            adp,
            output_port,
            input_port,
            justification,
            access_mode_id=access_mode_id,
            direct_grant=direct_grant,
            actor=actor,
        )
        if not existing:
            adp.input_ports.append(input_port)
        return input_port

    def _renew_single_input_port(
        self,
        adp: AbstractDataProduct,
        output_port_id: UUID,
        *,
        actor: User,
    ) -> InputPortModel:
        output_port = ensure_output_port_exists(
            output_port_id,
            self.db,
            options=[
                selectinload(OutputPortModel.data_product_links)
                .selectinload(InputPortModel.consuming_abstract_data_product)
                .selectinload(AbstractDataProduct.input_ports)
            ],
        )
        self._ensure_not_deleting(adp)
        self._ensure_not_deleting(output_port.data_product)
        existing = next(
            (link for link in adp.input_ports if link.output_port_id == output_port.id),
            None,
        )
        if existing is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Input port connection to Output Port ({output_port_id}) not found in {adp.abstract_data_product_type} {adp.id}",
            )
        if existing.pending_request is not None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="A request is already pending for this input port",
            )
        if (
            existing.active_grant is not None
            and existing.active_grant.valid_until is None
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="This input port already has permanent access; there is nothing to renew",
            )

        justification = existing.latest_request.justification
        access_mode_id = existing.latest_request.access_mode_id
        return self._create_request(
            adp,
            output_port,
            existing,
            justification,
            actor=actor,
            access_mode_id=access_mode_id,
        )

    def _get_adp_with_input_ports(self, id: UUID) -> AbstractDataProduct:
        adp = self.db.get(
            AbstractDataProduct,
            id,
            options=[
                selectinload(AbstractDataProduct.input_ports).selectinload(
                    InputPortModel.requests
                )
            ],
            populate_existing=True,
        )
        if not adp:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Abstract data product {id} not found",
            )
        return adp

    def request_input_ports(
        self,
        id: UUID,
        output_ports_requested: list[
            RequestInputPortsForAbstractDataProductRequestItem
        ],
        justification: str,
        *,
        actor: User,
    ) -> list[InputPortModel]:
        adp = self._get_adp_with_input_ports(id)
        input_ports = [
            self._add_single_input_port(
                adp,
                requested.output_port_id,
                justification,
                access_mode_id=requested.access_mode_id,
                actor=actor,
            )
            for requested in output_ports_requested
        ]
        self.db.flush()
        return input_ports

    def grant_output_port_access(
        self,
        consumer_id: UUID,
        data_product_id: UUID,
        output_port_id: UUID,
        justification: str,
        access_mode_id: Optional[UUID],
        *,
        actor: User,
    ) -> InputPortModel:
        return self._add_single_input_port(
            self._get_adp_with_input_ports(consumer_id),
            output_port_id,
            justification,
            access_mode_id=access_mode_id,
            data_product_id=data_product_id,
            direct_grant=True,
            actor=actor,
        )

    def renew_input_port(
        self,
        id: UUID,
        output_port_id: UUID,
        *,
        actor: User,
    ) -> InputPortModel:
        adp = self._get_adp_with_input_ports(id)
        input_port = self._renew_single_input_port(adp, output_port_id, actor=actor)
        self.db.flush()
        return input_port

    def renew_output_port_as_input_port(
        self,
        *,
        data_product_id: UUID,
        output_port_id: UUID,
        consuming_data_product_id: UUID,
        actor: User,
    ) -> RedactedInputPort:
        input_port_service = InputPortService(self.db)
        current_link = input_port_service.get_link(
            data_product_id,
            output_port_id,
            consuming_data_product_id,
            execution_options={"skip_data_product_visibility_filter": True},
        )
        self._ensure_not_deleting(current_link.consuming_abstract_data_product)
        self._ensure_not_deleting(current_link.output_port.data_product)
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
        access_duration = self._resolve_access_duration(
            current_link.consuming_abstract_data_product, current_link.output_port
        )
        now = datetime.now(timezone.utc)
        request = InputPortRequestModel(
            justification=previous_request.justification,
            requested_by_id=previous_request.requested_by_id,
            requested_on=now,
            access_duration_type=access_duration.access_duration_type,
            requested_duration_days=access_duration.days,
            input_port=current_link,
            access_mode_id=previous_request.access_mode_id,
        )
        self.db.add(request)
        self.db.flush()
        input_port_service.approve_request(request, now=now, decided_by=actor)

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
        return RedactedInputPort.of(current_link, previous_request.requested_by_id)

    def _get_input_port(self, id: UUID, output_port_id: UUID) -> InputPortModel:
        ensure_output_port_exists(output_port_id, self.db)
        adp = ensure_abstract_data_product_exists(
            id,
            self.db,
            options=[
                selectinload(AbstractDataProduct.input_ports).selectinload(
                    InputPortModel.requests
                )
            ],
            populate_existing=True,
        )
        input_port = next(
            (
                input_port
                for input_port in adp.input_ports
                if input_port.output_port_id == output_port_id
            ),
            None,
        )
        if not input_port:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Input port connection to Output Port ({output_port_id}) not found in {adp.abstract_data_product_type} {id}",
            )
        return input_port

    def revoke_input_port(
        self,
        id: UUID,
        output_port_id: UUID,
        *,
        actor: User,
    ) -> InputPortModel:
        input_port = self._get_input_port(id, output_port_id)
        target = input_port.active_grant
        if target is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="There is no active access to revoke",
            )

        target.revoked_by = actor
        target.revoked_at = datetime.now(tz=pytz.utc)
        input_port.recompute_status()
        self.db.flush()
        InputPortService(self.db)._sync_hidden_data_product_access(
            input_port.output_port.data_product_id
        )
        return input_port

    def cancel_input_port_request(
        self,
        id: UUID,
        output_port_id: UUID,
        *,
        actor: User,
    ) -> InputPortModel:
        input_port = self._get_input_port(id, output_port_id)
        target = input_port.pending_request
        if target is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="There is no pending request to cancel",
            )

        target.decided_by = actor
        target.decided_on = datetime.now(tz=pytz.utc)
        target.decision = InputPortRequestDecision.CANCELLED
        input_port.recompute_status()
        self.db.flush()
        return input_port

    def remove_input_port(
        self,
        id: UUID,
        output_port_id: UUID,
    ) -> InputPortModel:
        input_port = self._get_input_port(id, output_port_id)
        data_product_id = input_port.output_port.data_product_id
        self.db.delete(input_port)
        self.db.flush()
        InputPortService(self.db)._sync_hidden_data_product_access(data_product_id)
        return input_port

    def send_input_port_requested_emails_to_output_port_owners(
        self,
        input_ports: list[InputPortModel],
        background_tasks: BackgroundTasks,
        actor: User,
    ):
        for input_port in input_ports:
            if (
                input_port.output_port.access_function
                != OutputPortAccessFunction.UNRESTRICTED
            ):
                approvers = OutputPortRoleAssignmentService(
                    self.db
                ).users_with_authz_action(
                    input_port.output_port_id,
                    Action.OUTPUT_PORT__APPROVE_DATAPRODUCT_ACCESS_REQUEST,
                )
                other_approvers = [a for a in approvers if a != actor]
                if other_approvers:
                    background_tasks.add_task(
                        email.send_dataset_link_email(
                            input_port.consuming_abstract_data_product,
                            input_port.output_port,
                            requester=deepcopy(actor),
                            approvers=[
                                deepcopy(approver) for approver in other_approvers
                            ],
                        )
                    )

    def add_finalizer(self, id: UUID, finalizer: str) -> AbstractDataProduct:
        """Add a finalizer to the abstract data product.

        Finalizers block deletion until they are all removed.
        """
        adp = ensure_abstract_data_product_exists(id, self.db)
        if adp.status == AbstractDataProductStatus.DELETING:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"{adp.abstract_data_product_type.value} '{adp.name}' is already pending deletion",
            )
        if finalizer in (adp.finalizers or []):
            return adp
        adp.finalizers = list(adp.finalizers or []) + [finalizer]
        self.db.flush()
        return adp

    def mark_for_deletion(self, id: UUID) -> bool:
        """Mark the abstract data product as pending deletion.

        Returns True if deletion can proceed immediately (no finalizers),
        False if it has been marked as DELETING and must wait for finalizers.
        """
        adp = ensure_abstract_data_product_exists(id, self.db)
        if not adp.finalizers:
            return True
        adp.status = AbstractDataProductStatus.DELETING
        self.db.flush()
        return False

    def remove_finalizer(self, id: UUID, finalizer: str) -> bool:
        """Remove a finalizer from the abstract data product.

        Returns True if the caller should now perform the actual deletion
        (i.e., deletion_status is DELETING and no finalizers remain).
        """
        adp = ensure_abstract_data_product_exists(id, self.db)
        current = list(adp.finalizers or [])
        if finalizer not in current:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Finalizer '{finalizer}' not found",
            )
        current.remove(finalizer)
        adp.finalizers = current
        self.db.flush()
        return adp.status == AbstractDataProductStatus.DELETING and not current
