from copy import deepcopy
from datetime import datetime
from typing import Sequence

import pytz
from fastapi import BackgroundTasks, HTTPException
from sqlalchemy import UUID, select
from sqlalchemy.orm import Session, selectinload
from starlette import status

from app.abstract_data_product.model import (
    AbstractDataProduct,
    ensure_abstract_data_product_exists,
)
from app.authorization.role_assignments.enums import DecisionStatus
from app.authorization.role_assignments.output_port.service import (
    RoleAssignmentService as OutputPortRoleAssignmentService,
)
from app.core.authz import Action
from app.data_products import email
from app.data_products.output_ports.enums import OutputPortAccessType
from app.data_products.output_ports.input_ports.model import (
    InputPort as InputPortModel,
)
from app.data_products.output_ports.model import Dataset as OutputPortModel
from app.data_products.output_ports.model import ensure_output_port_exists
from app.data_products.output_ports.service import OutputPortService
from app.users.model import User


class AbstractDataProductService:
    def __init__(self, db: Session):
        self.db = db

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

    def request_input_port(
        self,
        consuming_abstract_data_product_id: UUID,
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
        data_product = self.db.get(
            AbstractDataProduct,
            consuming_abstract_data_product_id,
            options=[selectinload(AbstractDataProduct.input_ports)],
            populate_existing=True,
        )
        if not data_product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Abstract data product {consuming_abstract_data_product_id} not found",
            )

        if output_port.id in [
            link.dataset_id
            for link in data_product.input_ports
            if link.status != DecisionStatus.DENIED
        ]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Input port connection to Output Port ({output_port_id}) already exists in {data_product.abstract_data_product_type} {consuming_abstract_data_product_id}",
            )
        if output_port.data_product_id == data_product.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot link own dataset to data product",
            )

        if not OutputPortService(self.db).is_visible_to_user(output_port, actor):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have access to this private output port",
            )

        approval_status = (
            DecisionStatus.PENDING
            if output_port.access_type != OutputPortAccessType.UNRESTRICTED
            else DecisionStatus.APPROVED
        )

        dataset_link = InputPortModel(
            dataset_id=output_port_id,
            status=approval_status,
            justification=justification,
            requested_by=actor,
            requested_on=datetime.now(tz=pytz.utc),
        )
        data_product.input_ports.append(dataset_link)
        return dataset_link

    def request_input_ports(
        self,
        id: UUID,
        dataset_ids: list[UUID],
        justification: str,
        *,
        actor: User,
    ) -> list[InputPortModel]:
        dataset_links = [
            self.request_input_port(id, dataset_id, justification, actor=actor)
            for dataset_id in dataset_ids
        ]
        self.db.flush()
        return dataset_links

    def remove_input_port(
        self,
        id: UUID,
        dataset_id: UUID,
    ) -> InputPortModel:
        ensure_output_port_exists(dataset_id, self.db)
        adp = ensure_abstract_data_product_exists(
            id, self.db, options=[selectinload(AbstractDataProduct.input_ports)]
        )
        data_product_dataset = next(
            (
                dataset
                for dataset in adp.input_ports
                if dataset.dataset_id == dataset_id
            ),
            None,
        )
        if not data_product_dataset:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Data product dataset for data product {id} not found",
            )

        adp.input_ports.remove(data_product_dataset)
        self.db.commit()
        return data_product_dataset

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
