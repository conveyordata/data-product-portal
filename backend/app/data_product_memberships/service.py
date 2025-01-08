from datetime import datetime
from uuid import UUID

import pytz
from fastapi import BackgroundTasks, HTTPException, status
from sqlalchemy import asc
from sqlalchemy.orm import Session, joinedload

from app.core.aws.refresh_infrastructure_lambda import RefreshInfrastructureLambda
from app.core.email.send_mail import send_mail
from app.data_product_memberships.enums import (
    DataProductMembershipStatus,
    DataProductUserRole,
)
from app.data_product_memberships.model import DataProductMembership
from app.data_product_memberships.schema import DataProductMembershipCreate
from app.data_product_memberships.schema_get import DataProductMembershipGet
from app.data_products.model import DataProduct as DataProductModel
from app.data_products.model import ensure_data_product_exists
from app.data_products.service import DataProductService
from app.settings import settings
from app.users.model import ensure_user_exists
from app.users.schema import User


class DataProductMembershipService:
    @staticmethod
    def request_user_access_to_data_product(
        user_id: UUID,
        data_product_id: UUID,
        authenticated_user: User,
        db: Session,
        background_tasks: BackgroundTasks,
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

        url = (
            settings.HOST.strip("/")
            + "/data-products/"
            + str(data_product_id)
            + "#team"
        )
        owner_emails = [
            user.email for user in DataProductService().get_owners(data_product_id, db)
        ]
        background_tasks.add_task(
            send_mail,
            settings.FROM_MAIL_ADDRESS,
            owner_emails,
            f"{user.first_name} {user.last_name} "
            f"wants to join product {data_product.name}\n"
            f"Please approve or deny the request in the portal\n{url}",
            f"{user.first_name} {user.last_name} wants "
            f"to join project {data_product.name}",
        )
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
        RefreshInfrastructureLambda().trigger()
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

        data_product.memberships.remove(data_product_membership)
        db.commit()
        RefreshInfrastructureLambda().trigger()

    def add_data_product_membership(
        self,
        data_product_id: UUID,
        data_product_membership: DataProductMembershipCreate,
        db: Session,
        authenticated_user: User,
    ):
        data_product = ensure_data_product_exists(data_product_id, db)

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
        RefreshInfrastructureLambda().trigger()
        return {"id": data_product_membership.id}

    def update_data_product_membership_role(
        self,
        id: UUID,
        membership_role: DataProductUserRole,
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

        data_product_membership = db.get(DataProductMembership, id)
        data_product_membership.role = membership_role
        db.commit()
        db.refresh(data_product_membership)
        RefreshInfrastructureLambda().trigger()
        return {"id": data_product_membership.id}

    def get_user_pending_actions(
        self, db: Session, authenticated_user: User
    ) -> list[DataProductMembershipGet]:
        return (
            db.query(DataProductMembership)
            .options(
                joinedload(DataProductMembership.data_product),
                joinedload(DataProductMembership.user),
                joinedload(DataProductMembership.requested_by),
            )
            .filter(
                DataProductMembership.status
                == DataProductMembershipStatus.PENDING_APPROVAL
            )
            .filter(
                DataProductMembership.data_product.has(
                    DataProductModel.memberships.any(
                        user_id=authenticated_user.id, role=DataProductUserRole.OWNER
                    )
                )
            )
            .order_by(asc(DataProductMembership.requested_on))
            .all()
        )
