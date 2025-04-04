from typing import Optional
from uuid import UUID

from fastapi import Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session
from sqlalchemy.orm.exc import NoResultFound

from app.core.auth.auth import get_authenticated_user
from app.data_outputs.model import DataOutput as DataOutputModel
from app.data_product_memberships.enums import (
    DataProductMembershipStatus,
    DataProductUserRole,
)
from app.data_product_memberships.model import (
    DataProductMembership as DataProductMembershipModel,
)
from app.data_products.model import DataProduct as DataProductModel
from app.data_products_datasets.model import (
    DataProductDatasetAssociation as DataProductDatasetAssociationModel,
)
from app.database.database import get_db_session
from app.datasets.model import Dataset as DatasetModel
from app.users.schema import User


async def only_for_admin(authenticated_user: User = Depends(get_authenticated_user)):
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
    try:
        dataset = db.scalars(select(DatasetModel).filter_by(id=id)).one()
    except NoResultFound:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="dataset not found"
        )
    if authenticated_user not in dataset.owners and not authenticated_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is not an owner of the dataset",
        )


async def only_dataproduct_dataset_link_owners(
    id: UUID,
    authenticated_user: User = Depends(get_authenticated_user),
    db: Session = Depends(get_db_session),
):
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


async def only_data_output_owners(
    id: UUID,
    authenticated_user: User = Depends(get_authenticated_user),
    db: Session = Depends(get_db_session),
):
    data_output = db.get(DataOutputModel, id)
    if not data_output:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Data Output {id} not found",
        )
    return OnlyWithProductAccessID()(
        id=data_output.owner_id, authenticated_user=authenticated_user, db=db
    )


async def only_product_membership_owners(
    id: UUID,
    authenticated_user: User = Depends(get_authenticated_user),
    db: Session = Depends(get_db_session),
):
    try:
        membership = db.scalars(
            select(DataProductMembershipModel).filter_by(id=id)
        ).one()
    except NoResultFound:
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
        if data_product_id:
            id = data_product_id
        try:
            if id:
                data_product = db.scalars(
                    select(DataProductModel).filter_by(id=id)
                ).one()
            elif data_product_name:
                data_product = db.scalars(
                    select(DataProductModel).filter_by(namespace=data_product_name)
                ).one()
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Provide at least a product name or id",
                )
        except NoResultFound:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="product not found"
            )
        if (
            authenticated_user.id
            not in [
                membership.user_id
                for membership in data_product.memberships
                if membership.role in self.allowed_roles
                and membership.status == DataProductMembershipStatus.APPROVED
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
