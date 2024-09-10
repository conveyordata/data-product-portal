from typing import Optional
from uuid import UUID

from fastapi import Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session
from sqlalchemy.orm.exc import NoResultFound

from app.core.auth.auth import get_authenticated_user
from app.data_product_memberships.enums import DataProductUserRole
from app.data_products.model import DataProduct as DataProductModel
from app.database.database import get_db_session
from app.datasets.model import Dataset as DatasetModel
from app.users.schema import User


async def only_for_admin(authenticated_user: User = Depends(get_authenticated_user)):
    if not authenticated_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admin can execute this operation",
        )


async def only_with_dataset_access(
    id: Optional[UUID] = None,
    authenticated_user: User = Depends(get_authenticated_user),
    db: Session = Depends(get_db_session),
):
    try:
        if id:
            dataset = db.scalars(select(DatasetModel).filter_by(id=id)).one()
    except NoResultFound:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="dataset not founds"
        )
    if authenticated_user not in dataset.owners and not authenticated_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is not an owner of the dataset",
        )


class OnlyWithProductAccess:
    """Only allow users that have a membership of a certain role type to this product"""

    def __init__(self, allowed_roles: Optional[list[DataProductUserRole]] = None):
        if not allowed_roles:
            allowed_roles = [DataProductUserRole.OWNER, DataProductUserRole.MEMBER]
        self.allowed_roles = allowed_roles

    def __call__(
        self,
        data_product_name: Optional[str] = None,
        id: Optional[UUID] = None,
        authenticated_user: User = Depends(get_authenticated_user),
        db: Session = Depends(get_db_session),
    ) -> None:
        try:
            if id:
                data_product = db.scalars(
                    select(DataProductModel).filter_by(id=id)
                ).one()

            elif data_product_name:
                data_product = db.scalars(
                    select(DataProductModel).filter_by(external_id=data_product_name)
                ).one()
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Provide at least a product name or id",
                )
        except NoResultFound:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="product not founds"
            )
        if (
            authenticated_user.id
            not in [
                membership.user_id
                for membership in data_product.memberships
                if membership.role in self.allowed_roles
            ]
            and not authenticated_user.is_admin
        ):
            raise HTTPException(
                status.HTTP_403_FORBIDDEN,
                detail="You are not allowed to assume this role",
            )
