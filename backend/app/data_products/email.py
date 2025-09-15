import functools
from typing import Callable, Sequence
from uuid import UUID

import emailgen
from sqlalchemy.orm import Session

from app.core.email.send_mail import send_mail
from app.data_products.model import DataProduct
from app.datasets.model import Dataset
from app.settings import settings
from app.users.model import User as UserModel


def send_dataset_link_email(
    data_product: DataProduct,
    dataset: Dataset,
    *,
    requester_id: UUID,
    approver_ids: Sequence[UUID],
    db: Session,
) -> Callable[[None], None]:
    url = settings.HOST.strip("/") + "/datasets/" + str(dataset.id) + "#data-product"
    action = emailgen.Table(
        ["Data Product", "Request", "Dataset", "Owned By", "Requested By"]
    )
    requester = db.get(UserModel, requester_id)
    approvers = [db.get(UserModel, approver) for approver in approver_ids]
    action.add_row(
        [
            data_product.name,
            "Access to consume data from ",
            dataset.name,
            ", ".join(
                [
                    f"{approver.first_name} {approver.last_name}"
                    for approver in approvers
                ]
            ),
            f"{requester.first_name} {requester.last_name}",
        ]
    )

    return functools.partial(
        send_mail,
        recipient_ids=[approver.id for approver in approvers],
        action=action,
        url=url,
        subject=f"Action Required: {data_product.name} wants"
        f" to consume data from {dataset.name}",
        db=db,
    )
