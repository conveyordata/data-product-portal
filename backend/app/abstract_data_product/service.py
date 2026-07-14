from copy import deepcopy
from datetime import datetime
from typing import Sequence

import pytz
from fastapi import BackgroundTasks, HTTPException
from sqlalchemy import UUID, select
from sqlalchemy.orm import Session, selectinload
from starlette import status

from app.abstract_data_product.input_ports.enums import InputPortStatus
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
                    selectinload(InputPortModel.requests),
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
        if output_port.id in [
            link.dataset_id
            for link in adp.input_ports
            if link.status != DecisionStatus.DENIED
        ]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Input port connection to Output Port ({output_port_id}) already exists in {adp.abstract_data_product_type} {adp.id}",
            )
        if output_port.data_product_id == adp.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot link own dataset to data product",
            )

        if not OutputPortService(self.db).is_visible_to_user(output_port, actor):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have access to this private output port",
            )

        input_port_approval_status = (
            InputPortStatus.PENDING
            if output_port.access_type != OutputPortAccessType.UNRESTRICTED
            else InputPortStatus.APPROVED
        )
        input_port = InputPortModel(
            dataset_id=output_port_id,
            status=input_port_approval_status,
            consuming_abstract_data_product_id=adp.id,
        )
        request = InputPortRequestModel(
            justification=justification,
            requested_by=actor,
            requested_on=datetime.now(tz=pytz.utc),
            input_port=input_port,
        )
        if output_port.access_type == OutputPortAccessType.UNRESTRICTED:
            request.approve_input_port_request(
                now=datetime.now(tz=pytz.utc),
                decision_note="Auto approved for unrestricted output port",
            )
        else:
            request.decision = DecisionStatus.PENDING

        if request.decision == DecisionStatus.APPROVED and self.posthog:
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

        adp.input_ports.append(input_port)
        return input_port

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
        for input_port in input_ports:
            if input_port.dataset.access_type != OutputPortAccessType.UNRESTRICTED:
                approvers = OutputPortRoleAssignmentService(
                    self.db
                ).users_with_authz_action(
                    input_port.dataset_id,
                    Action.OUTPUT_PORT__APPROVE_DATAPRODUCT_ACCESS_REQUEST,
                )
                other_approvers = [a for a in approvers if a != actor]
                if other_approvers:
                    background_tasks.add_task(
                        email.send_dataset_link_email(
                            input_port.consuming_abstract_data_product,
                            input_port.dataset,
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
