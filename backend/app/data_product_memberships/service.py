from datetime import datetime
from typing import Sequence
from uuid import UUID

import emailgen
import pytz
from fastapi import BackgroundTasks, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.email.send_mail import send_mail
from app.data_product_memberships.enums import DataProductUserRole
from app.data_product_memberships.model import DataProductMembership
from app.data_products.model import ensure_data_product_exists
from app.data_products.service import DataProductService
from app.settings import settings
from app.users.model import ensure_user_exists
from app.users.schema import User


class DataProductMembershipService:
    def request_user_access_to_data_product(
        self,
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
        owners = [
            User.model_validate(owner)
            for owner in DataProductService().get_owners(data_product_id, db)
        ]
        action = emailgen.Table(["User", "Request", "Data Product", "Owned By"])
        action.add_row(
            [
                f"{user.first_name} {user.last_name}",
                "Wants to join ",
                data_product.name,
                ", ".join(
                    [f"{owner.first_name} {owner.last_name}" for owner in owners]
                ),
            ]
        )
        background_tasks.add_task(
            send_mail,
            owners,
            action,
            url,
            f"Action Required: {user.first_name} {user.last_name} wants "
            f"to join {data_product.name}",
        )
        return {"id": data_product_membership.id}

