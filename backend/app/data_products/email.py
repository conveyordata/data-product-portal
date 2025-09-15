import functools
from typing import Callable, Sequence

import emailgen

from app.core.email.send_mail import send_mail
from app.data_products.model import DataProduct
from app.datasets.model import Dataset
from app.settings import settings
from app.users.schema import User


def send_dataset_link_email(
    data_product: DataProduct,
    dataset: Dataset,
    *,
    requester: User,
    approvers: Sequence[User],
) -> Callable[[None], None]:
    url = settings.HOST.strip("/") + "/datasets/" + str(dataset.id) + "#data-product"
    action = emailgen.Table(
        ["Data Product", "Request", "Dataset", "Owned By", "Requested By"]
    )
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
        recipients=approvers,
        action=action,
        url=url,
        subject=f"Action Required: {data_product.name} wants"
        f" to consume data from {dataset.name}",
    )
