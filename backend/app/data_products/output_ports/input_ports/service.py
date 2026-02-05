import copy
from datetime import datetime
from typing import Sequence
from uuid import UUID

import pytz
from fastapi import HTTPException, status
from sqlalchemy import asc, select
from sqlalchemy.orm import Session

from app.authorization.role_assignments.enums import DecisionStatus
from app.authorization.role_assignments.output_port.model import (
    DatasetRoleAssignmentModel,
)
from app.core.authz import Action, Authorization
from app.data_products.output_ports.input_ports.model import (
    DataProductDatasetAssociation as DataProductDatasetAssociationModel,
)
from app.data_products.output_ports.model import Dataset
from app.data_products.output_ports.model import Dataset as DatasetModel
from app.pending_actions.schema import DataProductDatasetPendingAction
from app.users.schema import User


class DataProductDatasetService:
    def __init__(self, db: Session):
        self.db = db

    def get_link_by_id(self, id: UUID) -> DataProductDatasetAssociationModel:
        current_link = self.db.get(DataProductDatasetAssociationModel, id)
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
    ) -> DataProductDatasetAssociationModel:
        current_link = self.db.scalar(
            select(DataProductDatasetAssociationModel)
            .where(
                DataProductDatasetAssociationModel.data_product_id
                == consuming_data_product_id,
                DataProductDatasetAssociationModel.dataset_id == output_port_id,
            )
            .join(
                Dataset,
                Dataset.id == DataProductDatasetAssociationModel.dataset_id,
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
    ) -> DataProductDatasetAssociationModel:
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
        current_link.approved_on = datetime.now(tz=pytz.utc)
        self.db.commit()
        return current_link

    def deny_output_port_as_input_port(
        self,
        *,
        data_product_id: UUID,
        output_port_id: UUID,
        consuming_data_product_id: UUID,
        actor: User,
    ) -> DataProductDatasetAssociationModel:
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
        current_link.denied_on = datetime.now(tz=pytz.utc)
        self.db.commit()
        return current_link

    def remove_output_port_as_input_port(
        self,
        *,
        data_product_id: UUID,
        output_port_id: UUID,
        consuming_data_product_id: UUID,
    ) -> DataProductDatasetAssociationModel:
        current_link = self.get_link(
            data_product_id, output_port_id, consuming_data_product_id
        )
        result = copy.deepcopy(current_link)
        self.db.delete(current_link)
        self.db.commit()
        return result

    def get_user_pending_actions(
        self, user: User
    ) -> Sequence[DataProductDatasetPendingAction]:
        requested_associations = (
            self.db.scalars(
                select(DataProductDatasetAssociationModel)
                .where(
                    DataProductDatasetAssociationModel.status == DecisionStatus.PENDING
                )
                .where(
                    DataProductDatasetAssociationModel.dataset.has(
                        DatasetModel.assignments.any(
                            DatasetRoleAssignmentModel.user_id == user.id
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
            DataProductDatasetPendingAction.model_validate(a)
            for a in requested_associations
            if authorizer.has_access(
                sub=str(user.id),
                dom=str(a.dataset.data_product.domain),
                obj=str(a.dataset_id),
                act=Action.OUTPUT_PORT__APPROVE_DATAPRODUCT_ACCESS_REQUEST,
            )
        ]
