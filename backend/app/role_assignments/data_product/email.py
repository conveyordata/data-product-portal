from typing import Sequence

import emailgen

from app.core.email.send_mail import send_mail
from app.role_assignments.data_product.schema import (
    RoleAssignment,
)
from app.settings import settings
from app.users.schema import User


def send_role_assignment_request_email(
    role_assignment: RoleAssignment, approvers: Sequence[User]
) -> None:
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
        approvers,
        action,
        url,
        f"Action Required: {role_assignment.user.first_name} "
        f"{role_assignment.user.last_name} wants "
        f"to join {role_assignment.data_product.name}",
    )
