from typing import Optional
from uuid import UUID

from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.orm.exc import NoResultFound

from app.core.auth.auth import get_authenticated_user
from app.data_product_memberships.enums import DataProductUserRole
from app.data_products.model import DataProduct as DataProductModel
from app.database.database import get_db_session
from app.users.schema import User


async def only_for_admin(authenticated_user: User = Depends(get_authenticated_user)):
    if not authenticated_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admin can execute this operation",
        )


class OnlyProductRoles:
    """Only allow users that have a membership of a certain role type to this product"""

    def __init__(self, allowed_roles: list[DataProductUserRole]):
        if allowed_roles == [DataProductUserRole.MEMBER]:
            allowed_roles.append(DataProductUserRole.OWNER)
        self.allowed_roles = allowed_roles

    def __call__(
        self,
        data_product_name: Optional[str] = None,
        id: Optional[UUID] = None,
        authenticated_user: User = Depends(get_authenticated_user),
        db: Session = Depends(get_db_session),
    ) -> None:
        if id:
            try:
                data_product = db.get_one(DataProductModel, id)
            except NoResultFound:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail="product not founds"
                )
        elif data_product_name:
            data_product = db.query(DataProductModel).get_one(
                DataProductModel.external_id, data_product_name
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Provide at least a product name or id",
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
