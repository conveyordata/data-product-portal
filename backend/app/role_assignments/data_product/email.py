from typing import Sequence
from uuid import UUID

import emailgen
from sqlalchemy.orm import Session

from app.core.email.send_mail import send_mail
from app.role_assignments.data_product.model import (
    DataProductRoleAssignment as RoleAssignmentModel,
)
from app.settings import settings
from app.users.model import User as UserModel


def send_role_assignment_request_email(
    id: UUID, approver_ids: Sequence[UUID], db: Session
) -> None:
    role_assignment = db.get(RoleAssignmentModel, id)
    approvers = [db.get(UserModel, approver_id) for approver_id in approver_ids]

    url = (
        f"{settings.HOST.rstrip('/')}/data-products/"
        f"{role_assignment.data_product_id}#team"
    )
    action = emailgen.Table(["User", "Request", "Data Product", "Owned By"])
    action.add_row(
        [
            f"{role_assignment.user.first_name} {role_assignment.user.last_name}",
            "Wants to join ",
            role_assignment.data_product.name,
            ", ".join([f"{user.first_name} {user.last_name}" for user in approvers]),
        ]
    )

    return send_mail(
        [approver.id for approver in approvers],
        action,
        url,
        f"Action Required: {role_assignment.user.first_name} "
        f"{role_assignment.user.last_name} wants "
        f"to join {role_assignment.data_product.name}",
        db=db,
    )
