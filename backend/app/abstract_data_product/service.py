from copy import deepcopy
from datetime import datetime, timedelta
from typing import Optional, Sequence

import pytz
from fastapi import BackgroundTasks, HTTPException
from sqlalchemy import UUID, select
from sqlalchemy.orm import Session, selectinload
from starlette import status

from app.abstract_data_product.input_ports.model import (
    InputPort as InputPortModel,
)
from app.abstract_data_product.model import (
    AbstractDataProduct,
    ensure_abstract_data_product_exists,
)
from app.abstract_data_product.type import AbstractDataProductType
from app.access_durations.enums import AccessDurationType
from app.access_durations.service import AccessDurationService
from app.authorization.role_assignments.enums import DecisionStatus
from app.authorization.role_assignments.output_port.service import (
    RoleAssignmentService as OutputPortRoleAssignmentService,
)
from app.core.authz import Action
from app.core.logging.posthog_analytics import get_posthog_client
from app.data_products import email
from app.data_products.output_ports.enums import OutputPortAccessType
from app.data_products.output_ports.model import Dataset as OutputPortModel
from app.data_products.output_ports.model import ensure_output_port_exists
from app.data_products.output_ports.service import OutputPortService
from app.data_products.status import AbstractDataProductStatus
from app.users.model import User


class AbstractDataProductService:
    def __init__(self, db: Session):
        self.db = db
        self.posthog = get_posthog_client()

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
                .options(
                    selectinload(InputPortModel.dataset),
                )
                .filter(
                    InputPortModel.consuming_abstract_data_product_id == data_product_id
                ),
            )
            .unique()
            .all()
        )

    def _add_single_input_port(
        self,
        adp: AbstractDataProduct,
        output_port_id: UUID,
        justification: str,
        *,
        actor: User,
    ) -> InputPortModel:
        output_port = self._load_output_port_for_link(output_port_id)

        # Block if the consumer is being deleted
        self._ensure_not_deleting(adp)
        # Block if the output port's owning data product is being deleted
        self._ensure_not_deleting(output_port.data_product)
        renewal_link = self._renewal_link(adp, output_port)
        self._ensure_not_own_dataset(adp, output_port)
        self._ensure_visible_to_actor(output_port, actor)

        approval_status = self._approval_status_for(output_port)
        self._capture_approval_event(
            adp, output_port, output_port_id, approval_status, actor
        )
        time_bound = self._time_bound_fields(
            adp, output_port, approval_status, renewal_link, actor=actor
        )

        if renewal_link is None:
            return self._create_input_port(
                adp,
                output_port_id,
                justification,
                approval_status,
                time_bound,
                actor=actor,
            )
        return self._apply_renewal(
            renewal_link, approval_status, time_bound, actor=actor
        )

    def _load_output_port_for_link(self, output_port_id: UUID) -> OutputPortModel:
        return ensure_output_port_exists(
            output_port_id,
            self.db,
            options=[
                selectinload(OutputPortModel.data_product_links)
                .selectinload(InputPortModel.consuming_abstract_data_product)
                .selectinload(AbstractDataProduct.input_ports)
            ],
        )

    def _ensure_not_own_dataset(
        self, adp: AbstractDataProduct, output_port: OutputPortModel
    ) -> None:
        if output_port.data_product_id == adp.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot link own dataset to data product",
            )

    def _ensure_visible_to_actor(
        self, output_port: OutputPortModel, actor: User
    ) -> None:
        if not OutputPortService(self.db).is_visible_to_user(output_port, actor):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have access to this private output port",
            )

    def _approval_status_for(self, output_port: OutputPortModel) -> DecisionStatus:
        if output_port.access_type == OutputPortAccessType.UNRESTRICTED:
            return DecisionStatus.APPROVED
        return DecisionStatus.PENDING

    def _capture_approval_event(
        self,
        adp: AbstractDataProduct,
        output_port: OutputPortModel,
        output_port_id: UUID,
        approval_status: DecisionStatus,
        actor: User,
    ) -> None:
        if approval_status != DecisionStatus.APPROVED or not self.posthog:
            return
        self.posthog.capture(
            distinct_id=actor.id,
            event="Input Port Approved",
            properties={
                "data_product_id": str(output_port.data_product_id),
                "output_port_id": str(output_port_id),
                "consuming_data_product_id": str(adp.id),
                "type": str(adp.abstract_data_product_type.value),
            },
        )

    def _is_time_bound(
        self, adp: AbstractDataProduct, output_port: OutputPortModel
    ) -> bool:
        if adp.abstract_data_product_type == AbstractDataProductType.DATA_PRODUCT:
            return (
                output_port.data_product_access_duration_type
                == AccessDurationType.TIME_BOUND
            )
        if adp.abstract_data_product_type == AbstractDataProductType.EXPLORATION:
            return (
                output_port.exploration_access_duration_type
                == AccessDurationType.TIME_BOUND
            )
        return False

    def _access_duration_days(
        self, abstract_data_product_type: AbstractDataProductType
    ) -> int:
        access_duration_settings = AccessDurationService(
            self.db
        ).get_access_durations_by_type(
            abstract_data_product_type, AccessDurationType.TIME_BOUND
        )
        if (
            len(access_duration_settings) != 1
            or access_duration_settings[0].days is None
        ):
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Expected exactly one access duration setting for {abstract_data_product_type.value} with type {AccessDurationType.TIME_BOUND.value}, but found {len(access_duration_settings)}",
            )
        return access_duration_settings[0].days

    def _time_bound_fields(
        self,
        adp: AbstractDataProduct,
        output_port: OutputPortModel,
        approval_status: DecisionStatus,
        renewal_link: Optional[InputPortModel],
        *,
        actor: User,
    ) -> dict[str, int | datetime | User]:
        """Compute time-bound fields for a request.

        If approved, sets expires_on (and total_range_start for a fresh
        request, or renewed_by/renewed_on for a renewal). Otherwise, only
        requested_duration_days is set - the rest is filled in on approval.
        """
        if not self._is_time_bound(adp, output_port):
            return {}

        days = self._access_duration_days(adp.abstract_data_product_type)
        time_bound: dict[str, int | datetime | User] = {"requested_duration_days": days}
        if approval_status != DecisionStatus.APPROVED:
            return time_bound

        now = datetime.now(tz=pytz.utc)
        expires_on = now + timedelta(days=days)
        time_bound["expires_on"] = expires_on
        time_bound["total_range_end"] = expires_on
        if renewal_link is None:
            time_bound["total_range_start"] = now
        else:
            time_bound["renewed_by"] = actor
            time_bound["renewed_on"] = now
        return time_bound

    def _create_input_port(
        self,
        adp: AbstractDataProduct,
        output_port_id: UUID,
        justification: str,
        approval_status: DecisionStatus,
        time_bound: dict[str, int | datetime | User],
        *,
        actor: User,
    ) -> InputPortModel:
        input_port = InputPortModel(
            dataset_id=output_port_id,
            status=approval_status,
            justification=justification,
            requested_by=actor,
            requested_on=datetime.now(tz=pytz.utc),
            consuming_abstract_data_product_id=adp.id,
            **time_bound,
        )
        adp.input_ports.append(input_port)
        return input_port

    def _apply_renewal(
        self,
        renewal_link: InputPortModel,
        approval_status: DecisionStatus,
        time_bound: dict[str, int | datetime | User],
        *,
        actor: User,
    ) -> InputPortModel:
        if renewal_link.status == DecisionStatus.EXPIRED:
            renewal_link.status = approval_status

        # Still in flight until an approval decision extends the expiry below.
        renewal_link.is_renewing = approval_status != DecisionStatus.APPROVED
        if approval_status == DecisionStatus.APPROVED:
            renewal_link.expires_on = time_bound["expires_on"]
            renewal_link.renewed_by = actor
            renewal_link.renewed_on = datetime.now(tz=pytz.utc)
            renewal_link.total_range_end = time_bound["expires_on"]
        return renewal_link

    def _renewal_link(
        self, adp: AbstractDataProduct, output_port: OutputPortModel
    ) -> Optional[InputPortModel]:
        for link in adp.input_ports:
            if output_port.id == link.dataset_id:
                if link.status == DecisionStatus.DENIED:
                    continue
                elif link.status == DecisionStatus.EXPIRED or link.is_expiring_soon:
                    return link
                else:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Input port connection to Output Port ({output_port.id}) already exists in {adp.abstract_data_product_type} {adp.id}",
                    )
        return None

    def request_input_ports(
        self,
        id: UUID,
        output_port_ids: list[UUID],
        justification: str,
        *,
        actor: User,
    ) -> list[InputPortModel]:
        adp = self.db.get(
            AbstractDataProduct,
            id,
            options=[selectinload(AbstractDataProduct.input_ports)],
            populate_existing=True,
        )
        if not adp:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Abstract data product {id} not found",
            )
        input_ports = [
            self._add_single_input_port(adp, dataset_id, justification, actor=actor)
            for dataset_id in output_port_ids
        ]
        self.db.flush()
        return input_ports

    def remove_input_port(
        self,
        id: UUID,
        output_port_id: UUID,
    ) -> InputPortModel:
        ensure_output_port_exists(output_port_id, self.db)
        adp = ensure_abstract_data_product_exists(
            id,
            self.db,
            options=[selectinload(AbstractDataProduct.input_ports)],
            populate_existing=True,
        )
        input_port = next(
            (
                dataset
                for dataset in adp.input_ports
                if dataset.dataset_id == output_port_id
            ),
            None,
        )
        if not input_port:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Data product dataset for data product {id} not found",
            )

        self.db.delete(input_port)
        return input_port

    def send_input_port_requested_emails_to_output_port_owners(
        self,
        input_ports: list[InputPortModel],
        background_tasks: BackgroundTasks,
        actor: User,
    ):
        for dataset_link in input_ports:
            if dataset_link.dataset.access_type != OutputPortAccessType.UNRESTRICTED:
                approvers = OutputPortRoleAssignmentService(
                    self.db
                ).users_with_authz_action(
                    dataset_link.dataset_id,
                    Action.OUTPUT_PORT__APPROVE_DATAPRODUCT_ACCESS_REQUEST,
                )
                other_approvers = [a for a in approvers if a != actor]
                if other_approvers:
                    background_tasks.add_task(
                        email.send_dataset_link_email(
                            dataset_link.consuming_abstract_data_product,
                            dataset_link.dataset,
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
        self.db.commit()
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
        self.db.commit()
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
        self.db.commit()
        return adp.status == AbstractDataProductStatus.DELETING and not current
