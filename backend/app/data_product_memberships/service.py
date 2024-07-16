from datetime import datetime
from uuid import UUID

import pytz
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.data_product_memberships.enums import (
    DataProductMembershipStatus,
    DataProductUserRole,
)
from app.data_product_memberships.model import DataProductMembership
from app.data_product_memberships.schema import DataProductMembershipCreate
from app.data_products.model import ensure_data_product_exists
from app.data_products.schema import DataProduct
from app.users.model import ensure_user_exists
from app.users.schema import User


class DataProductMembershipService:

    @staticmethod
    def ensure_data_product_owner(authenticated_user: User, data_product: DataProduct):
        if authenticated_user.is_admin:
            return

        data_product_membership = next(
            (
                membership
                for membership in data_product.memberships
                if membership.user_id == authenticated_user.id
            ),
            None,
        )
        if (
            data_product_membership is None
            or data_product_membership.role != DataProductUserRole.OWNER
        ):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only owners can execute this operation",
            )

    @staticmethod
    def request_user_access_to_data_product(
        user_id: UUID,
        data_product_id: UUID,
        authenticated_user: User,
        db: Session,
    ):
        user = ensure_user_exists(user_id, db)
        data_product = ensure_data_product_exists(data_product_id, db)

        if user.id in [membership.user_id for membership in data_product.memberships]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"User {user_id} already exists in data_product {id}",
            )
        data_product_membership = DataProductMembership(
            user_id=user.id,
            role=DataProductUserRole.MEMBER,
            requested_by_id=authenticated_user.id,
            requested_on=datetime.now(tz=pytz.utc),
        )
        data_product.memberships.append(data_product_membership)
        db.commit()
        db.refresh(data_product_membership)

        return {"id": data_product_membership.id}

    def approve_membership_request(
        self,
        id: UUID,
        db: Session,
        authenticated_user: User,
    ):
        data_product_membership = (
            db.query(DataProductMembership).filter_by(id=id).first()
        )
        if data_product_membership is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Data product membership {id} not found",
            )
        data_product = data_product_membership.data_product
        self.ensure_data_product_owner(authenticated_user, data_product)

        if (
            data_product_membership.status
            != DataProductMembershipStatus.PENDING_APPROVAL
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Data product membership {id} is not in requested status",
            )

        data_product_membership.status = DataProductMembershipStatus.APPROVED
        data_product_membership.approved_by_id = authenticated_user.id
        data_product_membership.approved_on = datetime.now(tz=pytz.utc)
        db.commit()
        db.refresh(data_product_membership)

        return {"id": data_product_membership.id}

    def deny_membership_request(
        self,
        id: UUID,
        db: Session,
        authenticated_user: User,
    ):
        data_product_membership = (
            db.query(DataProductMembership).filter_by(id=id).first()
        )
        if data_product_membership is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Data product membership {id} not found",
            )
        data_product = data_product_membership.data_product
        self.ensure_data_product_owner(authenticated_user, data_product)

        if (
            data_product_membership.status
            != DataProductMembershipStatus.PENDING_APPROVAL
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Data product membership {id} is not in requested status",
            )

        data_product_membership.status = DataProductMembershipStatus.DENIED
        data_product_membership.denied_by_id = authenticated_user.id
        data_product_membership.denied_on = datetime.now(tz=pytz.utc)
        db.commit()
        db.refresh(data_product_membership)

        return {"id": data_product_membership.id}

    def remove_membership(self, id: UUID, db: Session, authenticated_user: User):
        data_product_membership = (
            db.query(DataProductMembership).filter_by(id=id).first()
        )
        if data_product_membership is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Data product membership {id} not found",
            )

        data_product = data_product_membership.data_product
        if data_product_membership.user_id != authenticated_user.id:
            self.ensure_data_product_owner(authenticated_user, data_product)

        data_product.memberships.remove(data_product_membership)
        db.commit()

    def add_data_product_membership(
        self,
        data_product_id: UUID,
        data_product_membership: DataProductMembershipCreate,
        db: Session,
        authenticated_user: User,
    ):
        data_product = ensure_data_product_exists(data_product_id, db)
        self.ensure_data_product_owner(authenticated_user, data_product)

        if data_product_membership.user_id in [
            membership.user_id for membership in data_product.memberships
        ]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"User {data_product_membership.user_id} "
                f"already exists in data_product {data_product_id}",
            )

        data_product_membership = DataProductMembership(
            **data_product_membership.dict(),
            status=DataProductMembershipStatus.APPROVED,
            requested_by_id=authenticated_user.id,
            requested_on=datetime.now(tz=pytz.utc),
            approved_by_id=authenticated_user.id,
            approved_on=datetime.now(tz=pytz.utc),
        )
        data_product.memberships.append(data_product_membership)
        db.commit()
        db.refresh(data_product_membership)
        return {"id": data_product_membership.id}

    def update_data_product_membership_role(
        self,
        id: UUID,
        membership_role: DataProductUserRole,
        authenticated_user: User,
        db: Session,
    ):
        data_product_membership = (
            db.query(DataProductMembership).filter_by(id=id).first()
        )
        if data_product_membership is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Data product membership {id} not found",
            )
        data_product = data_product_membership.data_product
        self.ensure_data_product_owner(authenticated_user, data_product)

        data_product_membership = db.get(DataProductMembership, id)
        data_product_membership.role = membership_role
        db.commit()
        db.refresh(data_product_membership)

        return {"id": data_product_membership.id}
