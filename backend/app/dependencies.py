from typing import Optional
from uuid import UUID

from fastapi import Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.core.auth.auth import get_authenticated_user
from app.data_outputs.model import DataOutput as DataOutputModel
from app.data_product_memberships.enums import DataProductUserRole
from app.data_product_memberships.model import (
    DataProductMembership as DataProductMembershipModel,
)
from app.data_products.model import DataProduct as DataProductModel
from app.data_products_datasets.model import (
    DataProductDatasetAssociation as DataProductDatasetAssociationModel,
)
from app.database.database import get_db_session
from app.datasets.model import Dataset as DatasetModel
from app.notifications.model import Notification as NotificationModel
from app.role_assignments.enums import DecisionStatus
from app.settings import settings
from app.users.schema import User


def only_for_admin(
    authenticated_user: User = Depends(get_authenticated_user),
):
    if settings.AUTHORIZER_ENABLED:
        return
    if not authenticated_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admin can execute this operation",
        )


def only_dataset_owners(
    id: UUID,
    authenticated_user: User = Depends(get_authenticated_user),
    db: Session = Depends(get_db_session),
):
    if settings.AUTHORIZER_ENABLED:
        return

    dataset = db.get(DatasetModel, id)

    if not dataset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="dataset not found"
        )
    if authenticated_user not in dataset.owners and not authenticated_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is not an owner of the dataset",
        )


def only_dataproduct_dataset_link_owners(
    id: UUID,
    authenticated_user: User = Depends(get_authenticated_user),
    db: Session = Depends(get_db_session),
):
    if settings.AUTHORIZER_ENABLED:
        return
    current_link = db.get(DataProductDatasetAssociationModel, id)
    if not current_link:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Dataset data product link {id} not found",
        )
    if (
        authenticated_user not in current_link.dataset.owners
        and not authenticated_user.is_admin
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only dataset owners can execute this action",
        )


def only_data_output_owners(
    id: UUID,
    authenticated_user: User = Depends(get_authenticated_user),
    db: Session = Depends(get_db_session),
):
    if settings.AUTHORIZER_ENABLED:
        return
    data_output = db.get(DataOutputModel, id)
    if not data_output:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Data Output {id} not found",
        )
    return OnlyWithProductAccessID()(
        id=data_output.owner_id, authenticated_user=authenticated_user, db=db
    )


def only_product_membership_owners(
    id: UUID,
    authenticated_user: User = Depends(get_authenticated_user),
    db: Session = Depends(get_db_session),
):
    if settings.AUTHORIZER_ENABLED:
        return

    membership = db.get(DataProductMembershipModel, id)

    if not membership:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="membership not found"
        )
    data_product_membership = next(
        (
            membership
            for membership in membership.data_product.memberships
            if membership.user_id == authenticated_user.id
        ),
        None,
    )
    if not authenticated_user.is_admin and (
        data_product_membership is None
        or data_product_membership.role != DataProductUserRole.OWNER
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is not an owner of the product for the membership request",
        )


def only_notification_owner(
    id: UUID,
    authenticated_user: User = Depends(get_authenticated_user),
    db: Session = Depends(get_db_session),
):
    notification = db.get(NotificationModel, id)

    if not notification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="notification not found"
        )
    if not authenticated_user.is_admin and (
        notification.user_id != authenticated_user.id
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Notification does not belong to authenticated user",
        )


class OnlyWithProductAccess:
    """Only allow users that have a membership of a certain role type to this product"""

    def __init__(self, allowed_roles: Optional[list[DataProductUserRole]] = None):
        if not allowed_roles:
            allowed_roles = [DataProductUserRole.OWNER, DataProductUserRole.MEMBER]
        self.allowed_roles = allowed_roles

    def call(
        self,
        data_product_name: Optional[str] = None,
        data_product_id: Optional[UUID] = None,
        id: Optional[UUID] = None,
        authenticated_user: User = Depends(get_authenticated_user),
        db: Session = Depends(get_db_session),
    ) -> None:
        if settings.AUTHORIZER_ENABLED:
            return
        if data_product_id:
            id = data_product_id
        if id:
            data_product = db.get(
                DataProductModel, id, options=[joinedload(DataProductModel.memberships)]
            )
        elif data_product_name:
            data_product = db.scalar(
                select(DataProductModel)
                .options(joinedload(DataProductModel.memberships))
                .filter_by(namespace=data_product_name)
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Provide at least a product name or id",
            )
        if not data_product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="product not found"
            )
        if (
            authenticated_user.id
            not in [
                membership.user_id
                for membership in data_product.memberships
                if membership.role in self.allowed_roles
                and membership.status == DecisionStatus.APPROVED
            ]
            and not authenticated_user.is_admin
        ):
            raise HTTPException(
                status.HTTP_403_FORBIDDEN,
                detail="You are not allowed to execute this operation",
            )


class OnlyWithProductAccessID(OnlyWithProductAccess):
    def __call__(
        self,
        id: UUID,
        authenticated_user: User = Depends(get_authenticated_user),
        db: Session = Depends(get_db_session),
    ) -> None:
        super().call(id=id, authenticated_user=authenticated_user, db=db)


class OnlyWithProductAccessDataProductID(OnlyWithProductAccess):
    def __call__(
        self,
        data_product_id: UUID,
        authenticated_user: User = Depends(get_authenticated_user),
        db: Session = Depends(get_db_session),
    ) -> None:
        super().call(
            data_product_id=data_product_id,
            authenticated_user=authenticated_user,
            db=db,
        )


class OnlyWithProductAccessName(OnlyWithProductAccess):
    def __call__(
        self,
        data_product_name: str,
        authenticated_user: User = Depends(get_authenticated_user),
        db: Session = Depends(get_db_session),
    ) -> None:
        super().call(
            data_product_name=data_product_name,
            authenticated_user=authenticated_user,
            db=db,
        )
